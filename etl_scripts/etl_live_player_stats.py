import sys, os

# 🔥 Make sure Python can see config_goat.py in your root directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config_goat import API_KEY, BASE_URL, HEADERS
from config import get_connection

import requests
import cx_Oracle
import time
# =========================================================
# SAFETY CONVERSION FUNCTIONS
# =========================================================
def safe_int(val):
    """Convert None, '', or null to 0 — prevents crashing."""
    try:
        return int(val) if val not in [None, ""] else 0
    except:
        return 0


def convert_minutes(value):
    """Convert 'MM:SS' → decimal minutes (example: '23:30' → 23.5)."""
    if not value:
        return 0
    
    try:
        if ":" in str(value):
            m, s = value.split(":")
            return int(m) + int(s)/60
        return float(value)
    except:
        return 0


# =========================================================
# 1) FETCH ACTIVE NBA PLAYERS
# =========================================================
def fetch_active_players(limit=300):
    players = []
    per_page = 100
    pages = limit // per_page

    print("\n📡 Fetching active NBA players...\n")

    for page in range(1, pages + 1):
        url = f"{BASE_URL}/players?per_page={per_page}&page={page}"
        response = requests.get(url, headers=HEADERS)

        if response.status_code != 200:
            print(f"❌ API ERROR Page {page}: {response.status_code}")
            break

        data = response.json()["data"]
        players.extend(data)

        print(f"📥 Page {page} loaded — Total players: {len(players)}")

        time.sleep(0.5)  # prevent rate limiting

    print(f"\n✅ Finished. Total active players retrieved: {len(players)}\n")
    return players


# =========================================================
# 2) GET GAME STATS FOR A PLAYER
# =========================================================
def fetch_player_stats(player_id, limit=50):
    url = f"{BASE_URL}/stats?player_ids[]={player_id}&per_page={limit}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        return []

    return response.json().get("data", [])


# =========================================================
# 3) SAVE ALL STATS TO ORACLE — FULLY SAFE VERSION
# =========================================================
def save_player_stats_to_oracle(stats):
    conn = get_connection()
    cursor = conn.cursor()

    insert_sql = """
        INSERT INTO NBA_PLAYER_LIVE_STATS
        (PLAYER_ID, GAME_DATE, POINTS, REBOUNDS, ASSISTS, STEALS, BLOCKS, MINUTES)
        VALUES (:1, TO_DATE(:2,'YYYY-MM-DD'), :3, :4, :5, :6, :7, :8)
    """

    batch = []
    for s in stats:
        batch.append([
            safe_int(s.get("player", {}).get("id")),
            s.get("game", {}).get("date", "")[:10],

            safe_int(s.get("pts")),
            safe_int(s.get("reb")),
            safe_int(s.get("ast")),
            safe_int(s.get("stl")),
            safe_int(s.get("blk")),
            convert_minutes(s.get("min"))
        ])

    cursor.executemany(insert_sql, batch)
    conn.commit()

    print(f"\n💾 Saved {len(batch)} new stat rows to Oracle.\n")

    cursor.close()
    conn.close()


# =========================================================
# MAIN EXECUTION PIPELINE
# =========================================================
if __name__ == "__main__":
    players = fetch_active_players(limit=300)  # adjust number anytime

    print("\n📊 Fetching live stats for players...\n")
    all_stats = []

    for p in players:
        pid = p["id"]
        name = f"{p['first_name']} {p['last_name']}"

        stats = fetch_player_stats(pid)

        if stats:
            print(f"📈 Loaded stats → {name} ({len(stats)} games)")
            all_stats.extend(stats)

        time.sleep(0.4)  # avoid API rate limits

    print(f"\n📁 Total Game Logs Retrieved: {len(all_stats)}\n")

    if all_stats:
        save_player_stats_to_oracle(all_stats)

    print("=======================================")
    print("   🔥 LIVE PLAYER STATS SYNCED 🔥")
    print("=======================================\n")
