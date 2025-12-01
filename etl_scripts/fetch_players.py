import sys, os
# Add the parent folder (D:\sports-data-intelligence) to Python’s search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import requests
from config import get_connection

def create_table(cursor):
    cursor.execute("""
        BEGIN
            EXECUTE IMMEDIATE 'CREATE TABLE players (
                id NUMBER PRIMARY KEY,
                first_name VARCHAR2(50),
                last_name VARCHAR2(50),
                position VARCHAR2(10),
                team_name VARCHAR2(100)
            )';
        EXCEPTION
            WHEN OTHERS THEN
                IF SQLCODE != -955 THEN
                    RAISE;
                END IF;
        END;
    """)

def insert_players(cursor, players):
    for p in players:
        try:
            cursor.execute("""
                INSERT INTO players (id, first_name, last_name, position, team_name)
                VALUES (:1, :2, :3, :4, :5)
            """, (
                p['id'],
                p['first_name'],
                p['last_name'],
                p['position'],
                p['team']['full_name']
            ))
        except Exception as e:
            if "ORA-00001" in str(e):
                # Duplicate key, skip it
                continue
            else:
                raise


def main():
    conn = get_connection()
    cursor = conn.cursor()

    # Create table
    create_table(cursor)
    print("🧱 Players table ready.")

    # Fetch player data from the API
    print("📡 Fetching data from API...")
    headers = {"Accept": "application/json","Authorization": "081aceca-0dd3-40f8-a617-bf5ce7212364"}
    response = requests.get("https://api.balldontlie.io/v1/players?per_page=50", headers=headers)
    print("HTTP Status:", response.status_code)
    print("Response text:", response.text[:200])  # shows first 200 chars

    data = response.json()['data']
    insert_players(cursor, data)
    conn.commit()
    print(f"✅ Inserted {len(data)} players into Oracle DB.")
    # Insert into Oracle
    insert_players(cursor, data)
    conn.commit()

    print(f"✅ Inserted {len(data)} players into Oracle DB.")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
