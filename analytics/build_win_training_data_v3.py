import pandas as pd
import numpy as np
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_connection

print("\n==============================")
print("📡 BUILDING WIN PREDICTOR V3")
print("==============================\n")

conn = get_connection()

# 1) Load recent game logs
game_logs = pd.read_sql("""
    SELECT GAME_DATE, HOME_TEAM, AWAY_TEAM, HOME_POINTS AS HS, AWAY_POINTS AS ASCORE
    FROM NBA_GAME_LOGS
    WHERE HOME_POINTS IS NOT NULL AND AWAY_POINTS IS NOT NULL
    ORDER BY GAME_DATE DESC
    FETCH FIRST 200 ROWS ONLY
""", conn)

print(f"📥 Loaded {len(game_logs)} games")

# 2) Load team season stats
team_stats = pd.read_sql("""
    SELECT TEAM_NAME, SEASON, WIN_PCT, POINTS
    FROM NBA_TEAM_STATS
""", conn)

print(f"📥 Loaded {len(team_stats)} team-season stat rows")

# 3) Load player scoring averages
player_ppg = pd.read_sql("""
    SELECT TEAM_NAME, AVG(POINTS) AS AVG_PTS
    FROM NBA_PLAYER_LIVE_STATS
    GROUP BY TEAM_NAME
""", conn)

print(f"📥 Loaded player impact rows: {len(player_ppg)}")

# Convert to lookup maps
team_map = team_stats.groupby(["TEAM_NAME","SEASON"]).agg({"WIN_PCT":"mean","POINTS":"mean"}).reset_index()
ppg_map = dict(zip(player_ppg.TEAM_NAME, player_ppg.AVG_PTS))

rows = []

for _, row in game_logs.iterrows():
    home, away, hs, ascore = row.HOME_TEAM, row.AWAY_TEAM, row.HS, row.ASCORE

    # Lookup win pct + season points if available (fallback safe)
    home_season = team_map[team_map.TEAM_NAME == home].head(1)
    away_season = team_map[team_map.TEAM_NAME == away].head(1)

    if home_season.empty or away_season.empty:
        continue

    rows.append({
        "HOME_WIN_PCT": float(home_season.WIN_PCT),
        "AWAY_WIN_PCT": float(away_season.WIN_PCT),
        "HOME_SEASON_PTS": float(home_season.POINTS),
        "AWAY_SEASON_PTS": float(away_season.POINTS),
        "HOME_PPG": ppg_map.get(home, 15),
        "AWAY_PPG": ppg_map.get(away, 15),

        # Target label
        "HOME_WIN_LABEL": 1 if hs > ascore else 0
    })

train = pd.DataFrame(rows)
OUT = "models/win_training_v3.csv"
train.to_csv(OUT, index=False)

print(f"\n🔥 TRAINING ROWS → {len(train)}")
print(f"💾 SAVED → {OUT}")
print("\n🚀 Run next:  python analytics/train_win_model_v3.py\n")
