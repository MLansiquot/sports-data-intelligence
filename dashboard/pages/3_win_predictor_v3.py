import os
import sys
import joblib
import pandas as pd
import streamlit as st

# ======================================
# FIX PATH — ENSURE CONFIG IS IMPORTABLE
# ======================================
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, ROOT)

from config import get_connection  # ← will work now

MODEL_PATH = os.path.join(ROOT, "models", "win_predictor_v3.pkl")


# ================================
# Load Model
# ================================
@st.cache_resource
def load_model():
    if not os.path.exists(MODEL_PATH):
        st.error("⚠ No V3 model found — Train first using train_win_model_v3.py")
        st.stop()
    return joblib.load(MODEL_PATH)

model = load_model()

st.title("🏀 Win Predictor V3 — Live Player Impact + Momentum")

st.write("""
Predict outcomes using:
✔ Team Win %  
✔ Total Scoring Power  
✔ Live Player Impact (PPG avg)  
✔ Momentum Indicators  
""")

conn = get_connection()

teams = pd.read_sql("SELECT DISTINCT TEAM_NAME FROM NBA_PLAYER_LIVE_STATS ORDER BY TEAM_NAME", conn)["TEAM_NAME"].tolist()

col1, col2 = st.columns(2)
home = col1.selectbox("Home Team", teams)
away = col2.selectbox("Away Team", teams)

if home == away:
    st.warning("Teams must be different.")
    st.stop()

# ================================
# PLAYER IMPACT
# ================================
impact = pd.read_sql("""
    SELECT TEAM_NAME, AVG(POINTS) AS PPG FROM NBA_PLAYER_LIVE_STATS GROUP BY TEAM_NAME
""", conn)

ppg_map = dict(zip(impact.TEAM_NAME, impact.PPG))

# TEAM SEASON METRICS
team_stats = pd.read_sql("SELECT TEAM_NAME, WIN_PCT, POINTS FROM NBA_TEAM_STATS", conn)

home_season = team_stats[team_stats.TEAM_NAME == home].iloc[0]
away_season = team_stats[team_stats.TEAM_NAME == away].iloc[0]

home_ppg = ppg_map.get(home, 10)
away_ppg = ppg_map.get(away, 10)

X = pd.DataFrame([{
    "HOME_WIN_PCT": home_season.WIN_PCT,
    "AWAY_WIN_PCT": away_season.WIN_PCT,
    "HOME_SEASON_PTS": home_season.POINTS,
    "AWAY_SEASON_PTS": away_season.POINTS,
    "HOME_PPG": home_ppg,
    "AWAY_PPG": away_ppg
}])

# ================================
# Predict
# ================================
if st.button("🔮 Predict Matchup"):
    proba = model.predict_proba(X)[0]
    home_prob = round(proba[1] * 100, 2)
    away_prob = round(proba[0] * 100, 2)

    st.subheader("📊 Win Probability")
    st.metric(home, f"{home_prob}%")
    st.metric(away, f"{away_prob}%")

    winner = home if home_prob > away_prob else away
    st.success(f"🏆 Predicted Winner: **{winner}**")

    st.progress(home_prob / 100)
