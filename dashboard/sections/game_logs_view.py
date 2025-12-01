import sys
import os

# Allow import of config.py from project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from config import get_connection


def render_game_logs_view():
    """Game logs explorer using NBA_GAME_LOGS."""

    conn = get_connection()

    # Seasons
    seasons_df = pd.read_sql(
        "SELECT DISTINCT SEASON FROM NBA_GAME_LOGS ORDER BY SEASON DESC",
        conn,
    )
    if seasons_df.empty:
        st.error("No data found in NBA_GAME_LOGS.")
        conn.close()
        return

    seasons = seasons_df["SEASON"].tolist()

    # Teams (from home + away)
    teams_df = pd.read_sql(
        """
        SELECT DISTINCT HOME_TEAM AS TEAM FROM NBA_GAME_LOGS
        UNION
        SELECT DISTINCT AWAY_TEAM AS TEAM FROM NBA_GAME_LOGS
        ORDER BY TEAM
        """,
        conn,
    )
    teams = teams_df["TEAM"].dropna().tolist()

    # Date range
    date_df = pd.read_sql(
        "SELECT MIN(GAME_DATE) AS MIN_DATE, MAX(GAME_DATE) AS MAX_DATE FROM NBA_GAME_LOGS",
        conn,
    )
    min_date = pd.to_datetime(date_df["MIN_DATE"].iloc[0]).date()
    max_date = pd.to_datetime(date_df["MAX_DATE"].iloc[0]).date()

    st.subheader("📅 Game Logs & Filters")

    col1, col2, col3 = st.columns(3)

    with col1:
        season_str = st.selectbox(
            "Season:",
            [str(s) for s in seasons],
            index=0,
            key="logs_season_select",
        )
        season = int(season_str)

    with col2:
        team_filter = st.selectbox(
            "Team (home or away):",
            ["All Teams"] + teams,
            index=0,
            key="logs_team_filter",
        )

    with col3:
        selected_range = st.date_input(
            "Date range:",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )
        if isinstance(selected_range, tuple):
            start_date, end_date = selected_range
        else:
            start_date, end_date = min_date, max_date

    # Build query
    sql = """
        SELECT GAME_ID,
               GAME_DATE,
               SEASON,
               HOME_TEAM,
               AWAY_TEAM,
               HOME_POINTS,
               AWAY_POINTS,
               WINNER,
               LOSER,
               HOME_STREAK,
               AWAY_STREAK,
               NOTES
        FROM NBA_GAME_LOGS
        WHERE SEASON = :season
          AND GAME_DATE BETWEEN :start_date AND :end_date
    """

    params = {
        "season": season,
        "start_date": start_date,
        "end_date": end_date,
    }

    if team_filter != "All Teams":
        sql += " AND (HOME_TEAM = :team OR AWAY_TEAM = :team)"
        params["team"] = team_filter

    df = pd.read_sql(sql, conn, params=params)
    conn.close()

    if df.empty:
        st.warning("No games match the selected filters.")
        return

    # Make date column prettier
    df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"]).dt.date

    # Summary metrics
    total_games = len(df)

    if team_filter != "All Teams":
        team = team_filter
        wins = (df["WINNER"] == team).sum()
        losses = (df["LOSER"] == team).sum()
        avg_points_for = (
            df.apply(
                lambda row: row["HOME_POINTS"]
                if row["HOME_TEAM"] == team
                else row["AWAY_POINTS"],
                axis=1,
            ).mean()
        )
        avg_points_against = (
            df.apply(
                lambda row: row["AWAY_POINTS"]
                if row["HOME_TEAM"] == team
                else row["HOME_POINTS"],
                axis=1,
            ).mean()
        )
    else:
        wins = None
        losses = None
        avg_points_for = (df["HOME_POINTS"] + df["AWAY_POINTS"]).mean()
        avg_points_against = None

    st.markdown("### 📊 Game Summary (Current Filters)")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Games", total_games)
    if team_filter != "All Teams":
        c2.metric("Team Record", f"{wins}–{losses}")
        c3.metric("Avg Points For", f"{avg_points_for:.1f}")
        c4.metric("Avg Points Against", f"{avg_points_against:.1f}")
    else:
        c2.metric("Teams in View", df["HOME_TEAM"].nunique() + df["AWAY_TEAM"].nunique())
        c3.metric("Avg Combined Points", f"{avg_points_for:.1f}")
        c4.metric("Filtered Season", season)

    st.divider()

    # Table view
    st.markdown("### 📋 Games")

    df_display = df[
        [
            "GAME_DATE",
            "HOME_TEAM",
            "AWAY_TEAM",
            "HOME_POINTS",
            "AWAY_POINTS",
            "WINNER",
            "LOSER",
            "NOTES",
        ]
    ].sort_values("GAME_DATE", ascending=False)

    st.dataframe(df_display, use_container_width=True, height=420)

    # Chart – combined points over time
    st.markdown("### 📈 Combined Points Over Time")

    df_chart = df.copy()
    df_chart["TOTAL_POINTS"] = df_chart["HOME_POINTS"] + df_chart["AWAY_POINTS"]

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df_chart["GAME_DATE"], df_chart["TOTAL_POINTS"], marker="o", linewidth=2)
    ax.set_xlabel("Game Date")
    ax.set_ylabel("Total Points")
    ax.set_title("Total Points per Game (Filtered)")
    ax.grid(True, linestyle="--", alpha=0.4)
    plt.xticks(rotation=45)
    st.pyplot(fig, use_container_width=True)
