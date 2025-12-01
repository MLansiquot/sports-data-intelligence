import cx_Oracle
import csv
import os
import sys

# Make sure Python can see config.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_connection


def load_game_logs(csv_path):
    """Load NBA game logs from CSV into Oracle."""

    if not os.path.exists(csv_path):
        print("❌ CSV file not found:", csv_path)
        return

    print(f"📂 Loading game logs from: {csv_path}")

    conn = get_connection()
    cursor = conn.cursor()

    with open(csv_path, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        headers = next(reader)  # skip header row

        inserted_rows = 0

        for row in reader:
            # Your CSV has **11 columns** — enforce that
            if len(row) != 11:
                print("⚠️ Skipping row with incorrect column count:", row)
                continue

            cursor.execute("""
                INSERT INTO NBA_GAME_LOGS (
                    GAME_DATE, SEASON, HOME_TEAM, AWAY_TEAM,
                    HOME_POINTS, AWAY_POINTS, WINNER, LOSER,
                    HOME_STREAK, AWAY_STREAK, NOTES
                )
                VALUES (
                    TO_DATE(:1, 'YYYY-MM-DD'),
                    :2, :3, :4, :5, :6, :7, :8, :9, :10, :11
                )
            """, row)

            inserted_rows += 1

    conn.commit()
    cursor.close()
    conn.close()

    print(f"✅ Successfully inserted {inserted_rows} game log records!")


if __name__ == "__main__":
    csv_path = r"D:\sports-data-intelligence\data\nba_game_logs\nba_game_logs.csv"
    load_game_logs(csv_path)

