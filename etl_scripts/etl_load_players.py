import requests
import sys, os
import cx_Oracle

# ensure config imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_connection
from config_goat import API_KEY, BASE_URL

HEADERS = {"Authorization": API_KEY}


def load_players(max_pages=25):
    conn = get_connection()
    cursor = conn.cursor()

    print("\n==============================")
    print(" 🏀 Starting Player Import")
    print("==============================")

    for page in range(1, max_pages + 1):
        print(f"\n📡 Requesting Page {page}...")

        url = f"{BASE_URL}/players?per_page=100&page={page}"
        response = requests.get(url, headers=HEADERS)

        if response.status_code != 200:
            print(f"❌ API Error {response.status_code} — stopping")
            break

        data = response.json()["data"]
        if not data:
            print("📭 No more players returned — ending.")
            break

        batch = []

        for p in data:
            batch.append([
                p["id"],
                p["first_name"],
                p["last_name"],
                p["team"]["full_name"] if p["team"] else None,
                p["position"],
                p.get("height"),
                p.get("weight")
            ])

        # ------------------ UPSERT FIX ------------------
        cursor.executemany("""
            MERGE INTO NBA_PLAYERS t
            USING (
                SELECT 
                    :1 AS PLAYER_ID,
                    :2 AS FIRST_NAME,
                    :3 AS LAST_NAME,
                    :4 AS TEAM_NAME,
                    :5 AS POSITION,
                    :6 AS HEIGHT,
                    :7 AS WEIGHT
                FROM dual
            ) s
            ON (t.PLAYER_ID = s.PLAYER_ID)

            WHEN MATCHED THEN 
                UPDATE SET 
                    t.TEAM_NAME = s.TEAM_NAME,
                    t.POSITION  = s.POSITION,
                    t.HEIGHT    = s.HEIGHT,
                    t.WEIGHT    = s.WEIGHT

            WHEN NOT MATCHED THEN
                INSERT (PLAYER_ID, FIRST_NAME, LAST_NAME, TEAM_NAME, POSITION, HEIGHT, WEIGHT)
                VALUES (s.PLAYER_ID, s.FIRST_NAME, s.LAST_NAME, s.TEAM_NAME, s.POSITION, s.HEIGHT, s.WEIGHT)
        """, batch)
        # ------------------------------------------------

        conn.commit()
        print(f"🟢 Inserted/Updated {len(data)} players")

    cursor.close()
    conn.close()
    print("\n==============================")
    print(" 🎉 Player Import Complete")
    print("==============================\n")


if __name__ == "__main__":
    load_players(max_pages=25)  # ~2500 players total
