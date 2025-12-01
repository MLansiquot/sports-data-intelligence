import os
import sys
import joblib
import pandas as pd
import streamlit as st

# Allow imports from project root (config, etc.)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_connection

# =====================================
# 🔁 Load V2 Momentum Model Artifact
# =====================================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "win_predictor_v2.pkl")

@st.cache_resource
def load_model_artifact():
    if not os.path.exists(MODEL_PATH):
        st.error(
            "Win Predictor V2 model not found.\n\n"
            "Train it first with:\n"
            "  1) python analytics\\build_win_training_data_v2.py\n"
            "  2) python analytics\\train_win_model_v2.py"
        )
        st.stop()
    return joblib.load(MODEL_PATH)

artifact = load_model_artifact()
model = artifact["model"]
feature_cols = artifact["feature_cols"]  # e.g. HOME_LAST10_WIN_PCT, etc.

# =====================================
# 🎨 Streamlit Page Setup
# =====================================
st.set_page_config(page_title="Win Predictor V3", page_icon="🔮", layout="wide")
st.title("🔮 NBA Win Predictor V3 — Momentum + Player Impact + Odds")

st.markdown(
    """
This version of the model uses **recent 10-game momentum** and lets you factor in:

- ⭐ **Key player impact** (using live player stats)
- 📉 **Sportsbook odds** (spread + moneylines, optional)
- 📈 Still powered by your trained V2 model (no retrain required yet)

The model prediction is still based on momentum features,  
but the **UI + explanation** incorporates star players and betting context.
"""
)

# =====================================
# 🗄️ Database Connection
# =====================================
conn = get_connection()

# -------------------------------------
# Helper: get list of teams that appear in logs
# -------------------------------------
teams_df = pd.read_sql(
    "SELECT DISTINCT HOME_TEAM AS TEAM FROM NBA_GAME_LOGS "
    "UNION SELECT DISTINCT AWAY_TEAM AS TEAM FROM NBA_GAME_LOGS "
    "ORDER BY TEAM",
    conn
)
teams = teams_df["TEAM"].tolist()

if not teams:
    st.error("No game logs found in NBA_GAME_LOGS — cannot run predictor V3.")
    conn.close()
    st.stop()

col_home, col_away = st.columns(2)

with col_home:
    home_team = st.selectbox("🏠 Home Team", teams, index=0)

with col_away:
    # different default to avoid identical teams
    default_away_index = 1 if len(teams) > 1 else 0
    away_team = st.selectbox(
        "🛫 Away Team",
        [t for t in teams if t != home_team] or teams,
        index=0
    )

if home_team == away_team:
    st.warning("Home and Away team must be different.")
    conn.close()
    st.stop()

st.markdown("---")

# =====================================
# 🧠 Momentum: Last-10 Team Form
# =====================================
def get_last10_form(team_name):
    """
    Returns a row with AVG_PTS and WIN_PCT over last 10 games (home+away combined).
    """
    q = """
        SELECT
            AVG(PTS) AS AVG_PTS,
            CASE 
                WHEN COUNT(*) = 0 THEN 0
                ELSE SUM(CASE WHEN PTS > OPP_PTS THEN 1 ELSE 0 END) / COUNT(*)
            END AS WIN_PCT
        FROM (
            SELECT
                HOME_TEAM AS TEAM,
                HOME_POINTS AS PTS,
                AWAY_POINTS AS OPP_PTS,
                GAME_DATE
            FROM NBA_GAME_LOGS
            WHERE HOME_TEAM = :team
            UNION ALL
            SELECT
                AWAY_TEAM AS TEAM,
                AWAY_POINTS AS PTS,
                HOME_POINTS AS OPP_PTS,
                GAME_DATE
            FROM NBA_GAME_LOGS
            WHERE AWAY_TEAM = :team
        )
        WHERE ROWNUM <= 10
    """
    df = pd.read_sql(q, conn, params={"team": team_name})
    if df.empty:
        return pd.Series({"AVG_PTS": 0.0, "WIN_PCT": 0.0})
    row = df.iloc[0]
    return pd.Series({
        "AVG_PTS": float(row["AVG_PTS"] or 0.0),
        "WIN_PCT": float(row["WIN_PCT"] or 0.0)
    })

home10 = get_last10_form(home_team)
away10 = get_last10_form(away_team)

st.subheader("📊 Recent Last-10 Game Momentum")

m1, m2 = st.columns(2)
with m1:
    st.markdown(f"**🏠 {home_team} — Last 10 Games**")
    st.metric("Win %", f"{home10.WIN_PCT*100:.1f}%")
    st.metric("Avg Points Scored", f"{home10.AVG_PTS:.1f}")

with m2:
    st.markdown(f"**🛫 {away_team} — Last 10 Games**")
    st.metric("Win %", f"{away10.WIN_PCT*100:.1f}%")
    st.metric("Avg Points Scored", f"{away10.AVG_PTS:.1f}")

st.markdown("---")

# =====================================
# ⭐ Player Impact (Top Scorers)
# =====================================
st.subheader("⭐ Player Impact — Top Scorers (Last Few Games)")

def get_team_top_players(team_name, limit_players=5, limit_games=10):
    """
    Returns top players by average points in NBA_PLAYER_LIVE_STATS
    joined with NBA_PLAYERS for the given team.
    """
    q = f"""
        SELECT *
        FROM (
            SELECT 
                p.ID AS PLAYER_ID,
                p.PLAYER_NAME,
                AVG(s.PTS) AS AVG_PTS,
                COUNT(*) AS GAMES
            FROM NBA_PLAYERS p
            JOIN NBA_PLAYER_LIVE_STATS s 
                ON s.PLAYER_ID = p.ID
            WHERE p.TEAM_NAME = :team
            GROUP BY p.ID, p.PLAYER_NAME
            ORDER BY AVG_PTS DESC
        )
        WHERE ROWNUM <= :limit_players
    """
    df = pd.read_sql(q, conn, params={"team": team_name, "limit_players": limit_players})
    # Clean nulls
    if not df.empty:
        df["AVG_PTS"] = df["AVG_PTS"].fillna(0.0)
    return df

home_players_df = get_team_top_players(home_team)
away_players_df = get_team_top_players(away_team)

c1, c2 = st.columns(2)

with c1:
    st.markdown(f"**🏠 {home_team} — Top Scorers**")
    if home_players_df.empty:
        st.info("No live player stats yet for this team.")
        home_star_name = None
        home_star_avg = 0.0
    else:
        st.dataframe(home_players_df[["PLAYER_NAME", "AVG_PTS", "GAMES"]], use_container_width=True)
        home_star_name = st.selectbox(
            "Select key home player (for impact)",
            ["(None)"] + home_players_df["PLAYER_NAME"].tolist(),
            index=1 if len(home_players_df) > 0 else 0
        )
        home_star_avg = float(
            home_players_df.loc[
                home_players_df["PLAYER_NAME"] == home_star_name, "AVG_PTS"
            ].iloc[0]
        ) if home_star_name and home_star_name != "(None)" else 0.0

with c2:
    st.markdown(f"**🛫 {away_team} — Top Scorers**")
    if away_players_df.empty:
        st.info("No live player stats yet for this team.")
        away_star_name = None
        away_star_avg = 0.0
    else:
        st.dataframe(away_players_df[["PLAYER_NAME", "AVG_PTS", "GAMES"]], use_container_width=True)
        away_star_name = st.selectbox(
            "Select key away player (for impact)",
            ["(None)"] + away_players_df["PLAYER_NAME"].tolist(),
            index=1 if len(away_players_df) > 0 else 0
        )
        away_star_avg = float(
            away_players_df.loc[
                away_players_df["PLAYER_NAME"] == away_star_name, "AVG_PTS"
            ].iloc[0]
        ) if away_star_name and away_star_name != "(None)" else 0.0

# Injury / status toggles
st.markdown("---")
st.subheader("🚑 Player Availability & Odds")

col_status1, col_status2 = st.columns(2)
with col_status1:
    home_star_out = st.checkbox(f"Is {home_star_name or 'home key player'} OUT or severely limited?", value=False)
with col_status2:
    away_star_out = st.checkbox(f"Is {away_star_name or 'away key player'} OUT or severely limited?", value=False)

# =====================================
# 💰 Sportsbook Odds (Manual input)
# =====================================
odds_col1, odds_col2, odds_col3 = st.columns(3)
with odds_col1:
    spread_home = st.number_input(
        "Home Spread (negative if favored, e.g. -4.5)",
        value=0.0,
        step=0.5
    )
with odds_col2:
    moneyline_home = st.number_input("Home Moneyline (e.g. -150)", value=0.0, step=10.0)
with odds_col3:
    moneyline_away = st.number_input("Away Moneyline (e.g. +130)", value=0.0, step=10.0)

st.caption("Odds are for **context/explanation only** in this version (not yet model features).")

st.markdown("---")

# =====================================
# 🧮 Build Model Features (with basic player-impact adjustment)
# =====================================
# Base momentum features
home_win_pct_10 = home10.WIN_PCT
away_win_pct_10 = away10.WIN_PCT
home_pts_10 = home10.AVG_PTS
away_pts_10 = away10.AVG_PTS

# Adjust team scoring if star is out:
# Simple heuristic: subtract a fraction of star's average
if home_star_out and home_star_avg > 0:
    home_pts_10_adj = max(0.0, home_pts_10 - 0.5 * home_star_avg)
    home_win_pct_10_adj = max(0.0, home_win_pct_10 * 0.9)
else:
    home_pts_10_adj = home_pts_10
    home_win_pct_10_adj = home_win_pct_10

if away_star_out and away_star_avg > 0:
    away_pts_10_adj = max(0.0, away_pts_10 - 0.5 * away_star_avg)
    away_win_pct_10_adj = max(0.0, away_win_pct_10 * 0.9)
else:
    away_pts_10_adj = away_pts_10
    away_win_pct_10_adj = away_win_pct_10

# Build input row consistent with V2 model features
X_input = pd.DataFrame([{
    "HOME_LAST10_WIN_PCT": home_win_pct_10_adj,
    "AWAY_LAST10_WIN_PCT": away_win_pct_10_adj,
    "HOME_LAST10_PTS": home_pts_10_adj,
    "AWAY_LAST10_PTS": away_pts_10_adj,
}])

# Make sure columns order matches what model expects
X_input = X_input[feature_cols]

# =====================================
# 🔮 Predict & Explain
# =====================================
if st.button("🔮 Predict Win Probability (V3 View)"):

    proba = model.predict_proba(X_input)[0]
    home_prob = round(float(proba[1]) * 100, 2)
    away_prob = round(float(proba[0]) * 100, 2)
    predicted_winner = home_team if home_prob > away_prob else away_team

    st.subheader("🔥 Prediction Result")
    st.success(f"**Predicted Winner:** {predicted_winner}")

    p1, p2 = st.columns(2)
    with p1:
        st.metric(f"{home_team} Win Probability", f"{home_prob}%")
    with p2:
        st.metric(f"{away_team} Win Probability", f"{away_prob}%")

    st.progress(home_prob / 100)

    # 🧠 Explanation
    st.markdown("### 🧠 Why This Prediction?")

    exp_df = pd.DataFrame([
        {
            "Factor": "Home Last-10 Win %",
            "Home": f"{home_win_pct_10_adj*100:.1f}%",
            "Away": ""
        },
        {
            "Factor": "Away Last-10 Win %",
            "Home": "",
            "Away": f"{away_win_pct_10_adj*100:.1f}%"
        },
        {
            "Factor": "Home Last-10 Avg PTS",
            "Home": f"{home_pts_10_adj:.1f}",
            "Away": ""
        },
        {
            "Factor": "Away Last-10 Avg PTS",
            "Home": "",
            "Away": f"{away_pts_10_adj:.1f}"
        },
        {
            "Factor": "Home Key Player",
            "Home": f"{home_star_name or 'N/A'} ({home_star_avg:.1f} PPG)" + (" — OUT" if home_star_out else ""),
            "Away": ""
        },
        {
            "Factor": "Away Key Player",
            "Home": "",
            "Away": f"{away_star_name or 'N/A'} ({away_star_avg:.1f} PPG)" + (" — OUT" if away_star_out else "")
        },
        {
            "Factor": "Market Spread (Home)",
            "Home": spread_home,
            "Away": ""
        },
        {
            "Factor": "Moneyline (Home / Away)",
            "Home": moneyline_home,
            "Away": moneyline_away
        },
    ])

    st.table(exp_df)

    # =============================
    # 📝 LOG PREDICTION (same table)
    # =============================
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO NBA_WIN_PREDICTIONS_LOG
            (HOME_TEAM, AWAY_TEAM, SEASON, HOME_WIN_PROB, AWAY_WIN_PROB,
             HOME_STREAK, AWAY_STREAK, HOME_WIN_PCT, AWAY_WIN_PCT,
             HOME_POINTS, AWAY_POINTS, PREDICTED_WINNER)
            VALUES (:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11,:12)
        """, [
            home_team,
            away_team,
            None,                     # SEASON not tied in this V3 view (can adjust later)
            home_prob,
            away_prob,
            None,                     # HOME_STREAK (not used here)
            None,                     # AWAY_STREAK
            home_win_pct_10_adj,
            away_win_pct_10_adj,
            home_pts_10_adj,
            away_pts_10_adj,
            predicted_winner
        ])
        conn.commit()
        cur.close()
        st.info("📄 Prediction logged to NBA_WIN_PREDICTIONS_LOG.")
    except Exception as e:
        st.warning(f"Could not log prediction: {e}")

# Close connection at end
conn.close()
