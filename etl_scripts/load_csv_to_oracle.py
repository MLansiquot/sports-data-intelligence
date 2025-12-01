import cx_Oracle
import csv
import os
from config import get_connection

def load_csv_to_oracle(csv_path):
    conn = get_connection()
    cursor = conn.cursor()

    print(f"📂 Loading data from {csv_path}")

    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cursor.execute("""
                INSERT INTO nba_team_stats (team_id, team_name, season, wins, losses, win_pct, points)
                VALUES (:1, :2, :3, :4, :5, :6, :7)
            """, (
                row['TEAM_ID'],
                row['TEAM_NAME'],
                2024,
                row['W'],
                row['L'],
                row['W_PCT'],
                row['PTS']
            ))

    conn.commit()
    print("✅ Data inserted successfully!")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    csv_path = r"D:\sports-data-intelligence\data\nba_team_stats\nba_team_stats.csv"
    if os.path.exists(csv_path):
        load_csv_to_oracle(csv_path)
    else:
        print("❌ CSV file not found. Check the path.")