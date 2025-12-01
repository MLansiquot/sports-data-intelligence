import streamlit as st
import cx_Oracle
import pandas as pd
import altair as alt

def connect():
    return cx_Oracle.connect("sports_analytics/123@localhost:1521/XEPDB1")

st.title("📈 Game Log Explorer")

player_id = st.number_input("Enter Player ID", min_value=1)

conn = connect()
df = pd.read_sql(f"""
    SELECT GAME_DATE, POINTS, REBOUNDS, ASSISTS
    FROM NBA_PLAYER_LIVE_STATS
    WHERE PLAYER_ID = {player_id}
    ORDER BY GAME_DATE
""", conn)

st.write(df)

chart = (
    alt.Chart(df)
    .mark_line(point=True)
    .encode(x="GAME_DATE:T", y="POINTS:Q")
)

st.altair_chart(chart, use_container_width=True)
