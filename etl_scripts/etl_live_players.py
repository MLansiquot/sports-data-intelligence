import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import cx_Oracle
from config import get_connection

API_URL = "https://api.balldontlie.io/v1/stats"
API_KEY = "YOUR_API_KEY_HERE"   # <- must be valid

headers = {"Authorization": f"Bearer {API_KEY}"}

def fetch_stats(page=1):
    response = requests.get(f"{API_URL}?per_page=100&page={page}", headers=headers)
    if response.status_code != 200:
        print("❌ API ERROR:", response.status_code)
        return []
    
    data = response.json().get("data", [])
    return data

def load_into_oracle(records):
    conn = get_connection()
    cursor = conn.cursor()

    for rec in records:
        try:
            cursor.execute("""
                INSERT INTO NBA_PLAYER_LIVE_STATS
                (PLAYER_ID, PLAYER_NAME, TEAM_NAME, SEASON, GAME_DATE,
                POINTS, REBOUNDS, ASSISTS, STEALS, BLOCKS, TURNOVERS, MINUTES)
                VALUES (:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11,:12)
            """, (
                rec["player"]["id"],
                rec["player"]["first_name"] + " " + rec["player"]["last_name"],
                rec["team"]["full_name"],
                rec["game"]["season"],
                rec["game"]["date"][:10],
                rec["pts"], rec["reb"], rec["ast"], rec["stl"], rec["blk"], rec["turnover"], rec["min"]
            ))
        except:
            continue

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    print("📡 Fetching live player stats…")
    data = fetch_stats()
    load_into_oracle(data)
    print("✅ Live stats inserted into Oracle!")
