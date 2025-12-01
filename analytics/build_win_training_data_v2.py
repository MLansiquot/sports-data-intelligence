import pandas as pd
import numpy as np
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_connection

print("\n📡 Building Win Predictor Training Dataset V2 — Momentum Based Model\n")

conn = get_connection()

# =======================
# LOAD GAME LOGS (IMPORTANT)
# =======================
game_logs = pd.read_sql("""
    SELECT GAME_DATE, SEASON, HOME_TEAM, AWAY_TEAM, HOME_POINTS, AWAY_POINTS,
           WINNER, LOSER
    FROM NBA_GAME_LOGS
    ORDER BY GAME_DATE DESC
    FETCH FIRST 5000 ROWS ONLY
""", conn)

print(f"📥 Loaded {len(game_logs)} games from DB")

# Convert date → datetime
game_logs["GAME_DATE"] = pd.to_datetime(game_logs["GAME_DATE"])


# =======================
# Helper: Last-10 form
# =======================
def last10_win_pct(team, date):
    df = game_logs[
        ((game_logs["HOME_TEAM"] == team) | (game_logs["AWAY_TEAM"] == team)) &
        (game_logs["GAME_DATE"] < date)
    ].sort_values("GAME_DATE").tail(10)

    if len(df) == 0:
        return 0.50  # neutral baseline if no history exists

    wins = (df["WINNER"] == team).sum()
    return wins / len(df)


def avg_points_last10(team, date):
    df = game_logs[
        ((game_logs["HOME_TEAM"] == team) | (game_logs["AWAY_TEAM"] == team)) &
        (game_logs["GAME_DATE"] < date)
    ].sort_values("GAME_DATE").tail(10)

    if len(df) == 0:
        return 100  # league average fallback

    pts = []
    for _, row in df.iterrows():
        pts.append(
            row.HOME_POINTS if row.HOME_TEAM == team else row.AWAY_POINTS
        )

    return np.mean(pts)


# =======================
# BUILD TRAINING ROWS
# =======================
training_rows = []

for idx, row in game_logs.iterrows():
    training_rows.append({
        "HOME_LAST10_WIN_PCT": last10_win_pct(row.HOME_TEAM, row.GAME_DATE),
        "AWAY_LAST10_WIN_PCT": last10_win_pct(row.AWAY_TEAM, row.GAME_DATE),
        "HOME_LAST10_PTS": avg_points_last10(row.HOME_TEAM, row.GAME_DATE),
        "AWAY_LAST10_PTS": avg_points_last10(row.AWAY_TEAM, row.GAME_DATE),
        "TARGET_WIN": 1 if row.WINNER == row.HOME_TEAM else 0
    })

df_train = pd.DataFrame(training_rows)

print(f"📊 Training Dataset Built — {len(df_train)} samples")
print(df_train.head())

df_train.to_csv("analytics/training_data_v2.csv", index=False)
print("\n💾 Saved → analytics/training_data_v2.csv\n")
