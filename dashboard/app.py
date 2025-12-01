import sys
import os

# Make sure we can import config.py from project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from utils.theme import apply_theme
from sections.team_view import render_team_view
from sections.players_view import render_players_view
from sections.game_logs_view import render_game_logs_view

# ---- Page config ----
st.set_page_config(
    page_title="Sports Data Intelligence – NBA",
    page_icon="🏀",
    layout="wide",
)

apply_theme()

st.title("🏀 Sports Data Intelligence – NBA Dashboard")
st.caption("Backed by Oracle 19c + Python + real NBA data")

# ---- Top controls ----
top_col1, top_col2 = st.columns([3, 1])

with top_col1:
    st.write("Use the tabs below to explore teams, players, and game logs.")

with top_col2:
    if st.button("🔄 Refresh data from Oracle"):
        st.rerun()

st.divider()

# ---- Main tabs ----
tab1, tab2, tab3 = st.tabs(
    [
        "📋 Team Overview & Standings",
        "👤 Player Overview (Live if available)",
        "📅 Game Logs & Filters",
    ]
)

with tab1:
    render_team_view()

with tab2:
    render_players_view()

with tab3:
    render_game_logs_view()
