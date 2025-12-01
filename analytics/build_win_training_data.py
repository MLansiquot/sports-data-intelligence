import os
import sys
import pandas as pd

# Make sure we can import config.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_connection


def build_training_data():
    """
    Build a training dataset for the win predictor from NBA_GAME_LOGS + NBA_TEAM_STATS.
    Label = 1 if home team wins, 0 if away team wins.
    """
    conn = get_connection()

    query = """
        SELECT
            g.GAME_ID,
            g.SEASON,
            g.HOME_TEAM,
            g.AWAY_TEAM,
            g.HOME_POINTS,
            g.AWAY_POINTS,
            g.HOME_STREAK,
            g.AWAY_STREAK,
            ht.WIN_PCT AS HOME_WIN_PCT,
            at.WIN_PCT AS AWAY_WIN_PCT,
            ht.POINTS  AS HOME_SEASON_POINTS,
            at.POINTS  AS AWAY_SEASON_POINTS,
            CASE 
                WHEN g.HOME_POINTS > g.AWAY_POINTS THEN 1 
                ELSE 0 
            END AS HOME_WIN_FLAG
        FROM NBA_GAME_LOGS g
        JOIN NBA_TEAM_STATS ht
          ON g.SEASON = ht.SEASON
         AND g.HOME_TEAM = ht.TEAM_NAME
        JOIN NBA_TEAM_STATS at
          ON g.SEASON = at.SEASON
         AND g.AWAY_TEAM = at.TEAM_NAME
    """

    print("🔗 Querying Oracle for training data...")
    df = pd.read_sql(query, conn)
    conn.close()

    if df.empty:
        print("⚠️ No rows returned. Check that NBA_GAME_LOGS and NBA_TEAM_STATS have data.")
        return

    # Basic cleanup
    numeric_cols = [
        "HOME_POINTS", "AWAY_POINTS",
        "HOME_STREAK", "AWAY_STREAK",
        "HOME_WIN_PCT", "AWAY_WIN_PCT",
        "HOME_SEASON_POINTS", "AWAY_SEASON_POINTS",
        "HOME_WIN_FLAG"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=numeric_cols)

    # Save to CSV
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)

    output_path = os.path.join(data_dir, "win_training_data.csv")
    df.to_csv(output_path, index=False)

    print(f"✅ Training data saved to: {output_path}")
    print(f"📊 Rows: {len(df)}, Columns: {len(df.columns)}")


if __name__ == "__main__":
    build_training_data()
