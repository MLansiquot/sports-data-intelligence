import sys, os, requests
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_connection

def create_table(cursor):
    cursor.execute("""
        BEGIN
            EXECUTE IMMEDIATE '
                CREATE TABLE games (
                    id NUMBER PRIMARY KEY,
                    game_date DATE,
                    home_team VARCHAR2(100),
                    home_score NUMBER,
                    visitor_team VARCHAR2(100),
                    visitor_score NUMBER
                )
            ';
        EXCEPTION
            WHEN OTHERS THEN
                IF SQLCODE != -955 THEN
                    RAISE;
                END IF;
        END;
    """)

def insert_games(cursor, games):
    for g in games:
        try:
            cursor.execute("""
                INSERT INTO games (id, game_date, home_team, home_score, visitor_team, visitor_score)
                VALUES (:1, TO_DATE(:2, 'YYYY-MM-DD'), :3, :4, :5, :6)
            """, (
                g['id'],
                g['date'],  # this is fine; Oracle stores it in game_date
                g['home_team']['full_name'],
                g['home_team_score'],
                g['visitor_team']['full_name'],
                g['visitor_team_score']
            ))
        except Exception as e:
            if "ORA-00001" in str(e):
                continue
            else:
                print(f"⚠️ Skipping record due to error: {e}")


def main():
    conn = get_connection()
    cursor = conn.cursor()
    create_table(cursor)
    print("🧱 Games table ready.")

    headers = {
        "Accept": "application/json",
        "Authorization": "081aceca-0dd3-40f8-a617-bf5ce7212364"  # Replace this with your real API key
    }

    print("📡 Fetching game data from API...")
    response = requests.get("https://api.balldontlie.io/v1/games?per_page=50", headers=headers)
    print("HTTP Status:", response.status_code)
    print("Response text:", response.text[:200])

    if response.status_code != 200:
        print("❌ API request failed.")
        return

    data = response.json()['data']
    insert_games(cursor, data)
    conn.commit()
    print(f"✅ Inserted {len(data)} games into Oracle DB.")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
