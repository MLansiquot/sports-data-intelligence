import os
import pandas as pd
from config import get_connection

# Default CSV path – update if needed
CSV_PATH = r"D:\sports-data-intelligence\data\nba_player_stats\nba_player_stats.csv"


def load_player_stats_from_csv(csv_path: str = CSV_PATH):
    print(f"📂 Looking for CSV at: {csv_path}")

    if not os.path.exists(csv_path):
        print("❌ CSV file not found. Check the path.")
        return

    # Read CSV
    df = pd.read_csv(csv_path)

    # Expected columns
    required_cols = [
        "PLAYER_NAME", "TEAM_NAME", "SEASON", "GAMES_PLAYED", "MINUTES",
        "POINTS", "ASSISTS", "REBOUNDS", "STEALS", "BLOCKS",
        "TURNOVERS", "FG_PERCENT", "THREE_PERCENT", "FT_PERCENT"
    ]

    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        print("❌ Missing required columns in CSV:", missing)
        print("   Make sure your header row matches exactly:")
        print("   " + ",".join(required_cols))
        return

    # Connect to Oracle
    conn = get_connection()
    cur = conn.cursor()

    # Optional: clear existing rows for seasons present in CSV
    seasons_in_csv = df["SEASON"].dropna().unique().tolist()
    if seasons_in_csv:
        print(f"🧹 Deleting existing rows for seasons: {seasons_in_csv}")
        cur.execute(
            f"DELETE FROM NBA_PLAYER_STATS WHERE SEASON IN ({','.join([':s'+str(i) for i in range(len(seasons_in_csv))])})",
            {f"s{i}": int(season) for i, season in enumerate(seasons_in_csv)}
        )
        conn.commit()

    insert_sql = """
        INSERT INTO NBA_PLAYER_STATS
        (PLAYER_NAME, TEAM_NAME, SEASON, GAMES_PLAYED, MINUTES, POINTS,
         ASSISTS, REBOUNDS, STEALS, BLOCKS, TURNOVERS, FG_PERCENT,
         THREE_PERCENT, FT_PERCENT)
        VALUES (:1, :2, :3, :4, :5, :6,
                :7, :8, :9, :10, :11, :12,
                :13, :14)
    """

    rows_inserted = 0

    for _, row in df.iterrows():
        try:
            cur.execute(
                insert_sql,
                (
                    row["PLAYER_NAME"],
                    row["TEAM_NAME"],
                    int(row["SEASON"]) if not pd.isna(row["SEASON"]) else None,
                    row["GAMES_PLAYED"],
                    row["MINUTES"],
                    row["POINTS"],
                    row["ASSISTS"],
                    row["REBOUNDS"],
                    row["STEALS"],
                    row["BLOCKS"],
                    row["TURNOVERS"],
                    row["FG_PERCENT"],
                    row["THREE_PERCENT"],
                    row["FT_PERCENT"],
                ),
            )
            rows_inserted += 1
        except Exception as e:
            print(f"⚠️ Skipping row for player {row.get('PLAYER_NAME', 'UNKNOWN')}: {e}")

    conn.commit()
    cur.close()
    conn.close()

    print(f"✅ Done. Inserted {rows_inserted} player rows into NBA_PLAYER_STATS.")


if __name__ == "__main__":
    load_player_stats_from_csv()
