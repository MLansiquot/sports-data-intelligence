import streamlit as st
import cx_Oracle

# Oracle connection helper
def connect():
    return cx_Oracle.connect("sports_analytics/123@localhost:1521/XEPDB1")

st.title("📊 Live NBA Player Stats Dashboard")

conn = connect()
cursor = conn.cursor()

# Dropdown list of active players
cursor.execute("SELECT DISTINCT PLAYER_ID FROM NBA_PLAYER_LIVE_STATS ORDER BY PLAYER_ID")
players = [row[0] for row in cursor.fetchall()]

player_id = st.selectbox("Select Player ID", players)

# Display latest 20 games
cursor.execute("""
    SELECT GAME_DATE, POINTS, REBOUNDS, ASSISTS, STEALS, BLOCKS, MINUTES
    FROM NBA_PLAYER_LIVE_STATS
    WHERE PLAYER_ID = :id
    ORDER BY GAME_DATE DESC FETCH NEXT 20 ROWS ONLY
""", {"id": player_id})

rows = cursor.fetchall()

st.subheader("📅 Last 20 Games")
st.table(rows)
