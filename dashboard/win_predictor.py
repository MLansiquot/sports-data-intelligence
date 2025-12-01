import os
import sys
import joblib
import pandas as pd
import streamlit as st

# allow oracle config import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_connection


# =====================================
# 🔥 Load V2 Momentum Model
# =====================================
MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "models",
    "win_predictor_v2.pkl"
)

@st.cache_resource
def load_model():
    if not os.path.exists(MODEL_PATH):
        st.error("Model not found — Train it using:\n"
                 "`python analytics/build_win_training_data_v2.py` then\n"
                 "`python analytics/train_win_model_v2.py`")
        st.stop()
    return joblib.load(MODEL_PATH)

artifact = load_model()
model = artifact["model"]
feature_cols = artifact["feature_cols"]  # Momentum features


# =====================================
# 🎨 Streamlit UI
# =====================================
st.set_page_config(page_title="Win Predictor V2", page_icon="🔮", layout="wide")
st.title("🔮 NBA Win Predictor V2 — Momentum Based")

st.markdown("""
This model predicts win probability using **recent 10-game performance**, including:

| Feature | Meaning |
|---|---|
| Home_Last10_Win% | Momentum + current form |
| Away_Last10_Win% | Consistency + fatigue indicator |
| Home_Last10_Points | Offensive rhythm recent scoring |
| Away_Last10_Points | Defensive breakdown vulnerability |

---
""")


# =====================================
# Get teams with live stats availability
# =====================================
conn = get_connection()

teams = pd.read_sql("""
    SELECT DISTINCT TEAM_NAME FROM NBA_PLAYER_LIVE_STATS
    JOIN NBA_PLAYERS ON NBA_PLAYERS.ID = NBA_PLAYER_LIVE_STATS.PLAYER_ID
    ORDER BY TEAM_NAME
""", conn)

team_list = teams["TEAM_NAME"].tolist()

home = st.selectbox("🏠 Home Team", team_list)
away = st.selectbox("🛫 Away Team", [t for t in team_list if t != home])

st.markdown("---")


# =====================================
# Fetch last 10 games team metrics
# =====================================
def last10(team):
    q = """
        SELECT
            AVG(PTS) AS AVG_PTS,
            SUM(CASE WHEN PTS > OPP_PTS THEN 1 ELSE 0 END)/10 AS WIN_PCT
        FROM (
            SELECT
                g.HOME_TEAM AS TEAM,
                g.HOME_POINTS AS PTS,
                g.AWAY_POINTS AS OPP_PTS
            FROM NBA_GAME_LOGS g WHERE HOME_TEAM = :team
            UNION ALL
            SELECT
                g.AWAY_TEAM AS TEAM,
                g.AWAY_POINTS AS PTS,
                g.HOME_POINTS AS OPP_PTS
            FROM NBA_GAME_LOGS g WHERE AWAY_TEAM = :team
        )
        WHERE ROWNUM <= 10
    """
    return pd.read_sql(q, conn, params={"team": team}).iloc[0]


st.subheader("📊 Recent Last-10-Game Form")

home10 = last10(home)
away10 = last10(away)

col1, col2 = st.columns(2)

with col1:
    st.metric("Home Last-10 Win %", round(home10.WIN_PCT*100,1))
    st.metric("Home Avg Points", round(home10.AVG_PTS,1))

with col2:
    st.metric("Away Last-10 Win %", round(away10.WIN_PCT*100,1))
    st.metric("Away Avg Points", round(away10.AVG_PTS,1))


# =====================================
# Build feature input for model
# =====================================
input_row = pd.DataFrame([{
    "HOME_LAST10_WIN_PCT": home10.WIN_PCT,
    "AWAY_LAST10_WIN_PCT": away10.WIN_PCT,
    "HOME_LAST10_PTS": home10.AVG_PTS,
    "AWAY_LAST10_PTS": away10.AVG_PTS
}])[feature_cols]

st.markdown("---")


# =====================================
# 🔮 Predict
# =====================================
if st.button("Predict Outcome"):

    probs = model.predict_proba(input_row)[0]
    homeProb = round(probs[1] * 100, 2)
    awayProb = round(probs[0] * 100, 2)

    winner = home if homeProb > awayProb else away

    st.success(f"**Predicted Winner:** {winner}")
    st.metric(f"{home} Win Probability", f"{homeProb}%")
    st.metric(f"{away} Win Probability", f"{awayProb}%")
    st.progress(homeProb/100)

    # Log to database
    conn.execute("""
        INSERT INTO NBA_WIN_PREDICTIONS_LOG
        (HOME_TEAM, AWAY_TEAM, HOME_WIN_PROB, AWAY_WIN_PROB, WINNER_PREDICTED)
        VALUES (:1,:2,:3,:4,:5)
    """, (home, away, homeProb, awayProb, winner))
    conn.commit()
    st.info("📄 Saved to prediction history.")


conn.close()
