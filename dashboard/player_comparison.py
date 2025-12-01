import os
import sys

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# Make sure we can import config.get_connection
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_connection

# ==============================
# Streamlit Page Setup
# ==============================
st.set_page_config(
    page_title="Player Comparison Engine",
    page_icon="🆚",
    layout="wide",
)

st.title("🆚 AI-Style Player Comparison Dashboard")
st.caption("Powered by Oracle 19c + Python + Streamlit (NBA Player Stats)")

st.markdown(
    """
Compare two players side-by-side using season averages from your Oracle table  
`NBA_PLAYER_STATS` (points, rebounds, assists, steals, blocks, shooting splits, etc.).
"""
)

# ==============================
# Load Player + Season Data
# ==============================
conn = get_connection()

players_df = pd.read_sql(
    "SELECT DISTINCT PLAYER_NAME FROM NBA_PLAYER_STATS ORDER BY PLAYER_NAME",
    conn,
)
seasons_df = pd.read_sql(
    "SELECT DISTINCT SEASON FROM NBA_PLAYER_STATS ORDER BY SEASON DESC",
    conn,
)

if players_df.empty or seasons_df.empty:
    st.error(
        "No data found in NBA_PLAYER_STATS.\n\n"
        "Make sure your player stats ETL has loaded data."
    )
    conn.close()
    st.stop()

players = players_df["PLAYER_NAME"].tolist()
seasons = seasons_df["SEASON"].tolist()

# ==============================
# Sidebar Controls
# ==============================
with st.sidebar:
    st.header("⚙️ Comparison Settings")

    season = st.selectbox("Season", seasons, index=0)

    player_a = st.selectbox("Player A", players, index=0)
    player_b = st.selectbox(
        "Player B",
        players,
        index=1 if len(players) > 1 else 0,
    )

    normalize_radar = st.checkbox(
        "Normalize radar values (0–1 scale)", value=True
    )

if player_a == player_b:
    st.warning("Please select two different players to compare.")
    conn.close()
    st.stop()

# ==============================
# Helper to fetch player row
# ==============================
def get_player_row(name, season):
    query = """
        SELECT PLAYER_NAME, TEAM_NAME, SEASON,
               GAMES_PLAYED, MINUTES, POINTS, ASSISTS,
               REBOUNDS, STEALS, BLOCKS, TURNOVERS,
               FG_PERCENT, THREE_PERCENT, FT_PERCENT
        FROM NBA_PLAYER_STATS
        WHERE PLAYER_NAME = :name AND SEASON = :season
    """
    df = pd.read_sql(query, conn, params={"name": name, "season": season})
    return df.iloc[0] if not df.empty else None


row_a = get_player_row(player_a, season)
row_b = get_player_row(player_b, season)

if row_a is None or row_b is None:
    st.error(
        "Could not find stats for one or both players in this season.\n\n"
        f"Season: {season}\n"
        f"A: {player_a} -> {'FOUND' if row_a is not None else 'MISSING'}\n"
        f"B: {player_b} -> {'FOUND' if row_b is not None else 'MISSING'}\n"
    )
    conn.close()
    st.stop()

# We no longer need the DB connection
conn.close()

# ==============================
# Summary Header
# ==============================
col_a, col_mid, col_b = st.columns([3, 1, 3])

with col_a:
    st.markdown(f"### 🧍 Player A: **{row_a['PLAYER_NAME']}**")
    st.markdown(f"**Team:** {row_a['TEAM_NAME']}")
    st.markdown(f"**Season:** {int(row_a['SEASON'])}")

with col_mid:
    st.markdown("<h2 style='text-align:center;'>VS</h2>", unsafe_allow_html=True)

with col_b:
    st.markdown(f"### 🧍 Player B: **{row_b['PLAYER_NAME']}**")
    st.markdown(f"**Team:** {row_b['TEAM_NAME']}")
    st.markdown(f"**Season:** {int(row_b['SEASON'])}")

st.markdown("---")

# ==============================
# Core Numeric Metrics
# ==============================
metrics = [
    ("Points",       "POINTS"),
    ("Rebounds",     "REBOUNDS"),
    ("Assists",      "ASSISTS"),
    ("Steals",       "STEALS"),
    ("Blocks",       "BLOCKS"),
    ("Turnovers",    "TURNOVERS"),
    ("Minutes",      "MINUTES"),
]

shooting = [
    ("FG%",    "FG_PERCENT"),
    ("3P%",    "THREE_PERCENT"),
    ("FT%",    "FT_PERCENT"),
]

st.markdown("### 📊 Per-Game Production")

mcol_a, mcol_b = st.columns(2)

with mcol_a:
    st.markdown(f"#### {row_a['PLAYER_NAME']}")
    for label, col in metrics:
        val = row_a[col]
        st.write(f"- **{label}:** {val:.1f}" if val is not None else f"- **{label}:** N/A")

with mcol_b:
    st.markdown(f"#### {row_b['PLAYER_NAME']}")
    for label, col in metrics:
        val = row_b[col]
        st.write(f"- **{label}:** {val:.1f}" if val is not None else f"- **{label}:** N/A")

st.markdown("### 🎯 Shooting Splits")

scol_a, scol_b = st.columns(2)

with scol_a:
    st.markdown(f"#### {row_a['PLAYER_NAME']}")
    for label, col in shooting:
        val = row_a[col]
        st.write(f"- **{label}:** {val*100:.1f}%" if val is not None else f"- **{label}:** N/A")

with scol_b:
    st.markdown(f"#### {row_b['PLAYER_NAME']}")
    for label, col in shooting:
        val = row_b[col]
        st.write(f"- **{label}:** {val*100:.1f}%" if val is not None else f"- **{label}:** N/A")

st.markdown("---")

# ==============================
# 🕸 Radar Chart Comparison
# ==============================
st.markdown("### 🕸 Visual Comparison (Radar Chart)")

radar_stats_labels = ["POINTS", "REBOUNDS", "ASSISTS", "STEALS", "BLOCKS"]
radar_display_names = ["PTS", "REB", "AST", "STL", "BLK"]

vals_a = np.array([row_a[s] if row_a[s] is not None else 0 for s in radar_stats_labels], dtype=float)
vals_b = np.array([row_b[s] if row_b[s] is not None else 0 for s in radar_stats_labels], dtype=float)

if normalize_radar:
    combined_max = np.maximum(vals_a, vals_b)
    combined_max[combined_max == 0] = 1.0
    vals_a_norm = vals_a / combined_max
    vals_b_norm = vals_b / combined_max
    plot_vals_a = vals_a_norm
    plot_vals_b = vals_b_norm
else:
    plot_vals_a = vals_a
    plot_vals_b = vals_b

N = len(radar_stats_labels)
angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
plot_vals_a = np.concatenate((plot_vals_a, [plot_vals_a[0]]))
plot_vals_b = np.concatenate((plot_vals_b, [plot_vals_b[0]]))
angles += angles[:1]

fig, ax = plt.subplots(subplot_kw={"polar": True}, figsize=(7, 6))

ax.plot(angles, plot_vals_a, linewidth=2, label=row_a["PLAYER_NAME"])
ax.fill(angles, plot_vals_a, alpha=0.25)

ax.plot(angles, plot_vals_b, linewidth=2, label=row_b["PLAYER_NAME"])
ax.fill(angles, plot_vals_b, alpha=0.25)

ax.set_thetagrids(np.degrees(angles[:-1]), radar_display_names)
ax.set_title("Per-Game Impact Comparison", pad=20)
ax.grid(True, linestyle="--", alpha=0.5)
ax.legend(loc="upper right", bbox_to_anchor=(1.2, 1.1))

st.pyplot(fig, use_container_width=True)

# ==============================
# 🧾 Simple Text Verdict
# ==============================
st.markdown("### 🧾 Quick Comparison Summary")

def compare_stat(label, col):
    va = row_a[col] if row_a[col] is not None else 0
    vb = row_b[col] if row_b[col] is not None else 0
    if va > vb:
        return f"- **{label}:** Advantage **{row_a['PLAYER_NAME']}** ({va:.1f} vs {vb:.1f})"
    elif vb > va:
        return f"- **{label}:** Advantage **{row_b['PLAYER_NAME']}** ({vb:.1f} vs {va:.1f})"
    else:
        return f"- **{label}:** Even ({va:.1f} vs {vb:.1f})"

summary_lines = [
    compare_stat("Scoring (PTS)", "POINTS"),
    compare_stat("Rebounding (REB)", "REBOUNDS"),
    compare_stat("Playmaking (AST)", "ASSISTS"),
    compare_stat("Defense (STL)", "STEALS"),
    compare_stat("Rim Protection (BLK)", "BLOCKS"),
]

for line in summary_lines:
    st.write(line)

st.info(
    "This comparison uses per-game season averages. "
    "Later you can extend this to use **live stats**, advanced metrics (PER, WS, BPM), "
    "or your AI models for **overall impact scoring**."
)
