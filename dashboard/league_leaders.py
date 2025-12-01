import streamlit as st
import cx_Oracle
import pandas as pd

def connect():
    return cx_Oracle.connect("sports_analytics/123@localhost:1521/XEPDB1")

st.title("🏀 NBA League Leaders")

metric = st.selectbox("Sort By", ["POINTS", "REBOUNDS", "ASSISTS", "STEALS", "BLOCKS"])

query = f"""
    SELECT PLAYER_ID, AVG({metric}) AS AVG_STAT
    FROM NBA_PLAYER_LIVE_STATS
    GROUP BY PLAYER_ID
    ORDER BY AVG_STAT DESC FETCH FIRST 10 ROWS ONLY
"""

conn = connect()
df = pd.read_sql(query, conn)

st.subheader(f"Top 10 in {metric}")
st.table(df)
