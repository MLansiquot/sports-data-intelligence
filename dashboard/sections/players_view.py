import sys
import os

# Allow import of config.py from project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from config import get_connection


def _get_player_source_table(conn) -> str | None:
    """
    Decide whether to use live stats or base stats.
    Priority:
      1. NBA_PLAYER_LIVE_STATS (if exists and has rows)
      2. NBA_PLAYER_STATS
    """
    for table in ["NBA_PLAYER_LIVE_STATS", "NBA_PLAYER_STATS"]:
        try:
            df = pd.read_sql(f"SELECT COUNT(*) AS CNT FROM {table}", conn)
            if df["CNT"].iloc[0] > 0:
                return table
        except Exception:
            # Table might not exist yet
            continue
    return None


def render_players_view():
    """Player overview: top scorers/rebounders/passers for a season."""

    conn = get_connection()

    source_table = _get_player_source_table(conn)
    if not source_table:
        st.error(
            "No player stats found. Make sure NBA_PLAYER_STATS or "
            "NBA_PLAYER_LIVE_STATS has data."
        )
        conn.close()
        return

    if source_table == "NBA_PLAYER_LIVE_STATS":
        st.info("Using LIVE player stats (NBA_PLAYER_LIVE_STATS).")
    else:
        st.info("Using base player stats table (NBA_PLAYER_STATS).")

    # Load available seasons + teams from chosen table
    seasons_df = pd.read_sql(
        f"SELECT DISTINCT SEASON FROM {source_table} ORDER BY SEASON DESC",
        conn,
    )
    teams_df = pd.read_sql(
        f"SELECT DISTINCT TEAM_NAME FROM {source_table} ORDER BY TEAM_NAME",
        conn,
    )

    if seasons_df.empty:
        st.error(f"No seasons available in {source_table}.")
        conn.close()
        return

    seasons = seasons_df["SEASON"].tolist()
    teams = teams_df["TEAM_NAME"].dropna().tolist()

    season_str = st.selectbox(
        "Season:",
        [str(s) for s in seasons],
        index=0,
        key="player_season_select",
    )
    season = int(season_str)

    team_filter = st.selectbox(
        "Filter by team (optional):",
        ["All Teams"] + teams,
        index=0,
        key="player_team_filter",
    )

    # Build query
    base_sql = f"""
        SELECT PLAYER_NAME, TEAM_NAME, SEASON,
               GAMES_PLAYED, MINUTES, POINTS, ASSISTS, REBOUNDS,
               STEALS, BLOCKS, TURNOVERS,
               FG_PERCENT, THREE_PERCENT, FT_PERCENT
        FROM {source_table}
        WHERE SEASON = :season
    """

    params = {"season": season}

    if team_filter != "All Teams":
        base_sql += " AND TEAM_NAME = :team"
        params["team"] = team_filter

    df = pd.read_sql(base_sql, conn, params=params)
    conn.close()

    if df.empty:
        st.warning("No player stats match the selected filters.")
        return

    # Per-game metrics
    df["GAMES_PLAYED"] = df["GAMES_PLAYED"].replace(0, pd.NA)
    df["PTS_PG"] = (df["POINTS"] / df["GAMES_PLAYED"]).round(1)
    df["AST_PG"] = (df["ASSISTS"] / df["GAMES_PLAYED"]).round(1)
    df["REB_PG"] = (df["REBOUNDS"] / df["GAMES_PLAYED"]).round(1)

    # Summary metrics
    st.subheader("📊 Player Stats Summary")

    total_players = len(df)
    avg_pts = df["PTS_PG"].mean()
    avg_ast = df["AST_PG"].mean()
    avg_reb = df["REB_PG"].mean()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Players in View", total_players)
    c2.metric("Avg Points / Game", f"{avg_pts:.1f}")
    c3.metric("Avg Assists / Game", f"{avg_ast:.1f}")
    c4.metric("Avg Rebounds / Game", f"{avg_reb:.1f}")

    st.divider()

    # Top players by category
    st.subheader("🏆 Leaders (Current Filters)")

    top_pts = df.sort_values("PTS_PG", ascending=False).head(5)
    top_ast = df.sort_values("AST_PG", ascending=False).head(5)
    top_reb = df.sort_values("REB_PG", ascending=False).head(5)

    col_pts, col_ast, col_reb = st.columns(3)

    with col_pts:
        st.markdown("**Top Scorers (PTS/G)**")
        st.dataframe(
            top_pts[["PLAYER_NAME", "TEAM_NAME", "PTS_PG", "GAMES_PLAYED"]],
            hide_index=True,
            use_container_width=True,
        )

    with col_ast:
        st.markdown("**Top Playmakers (AST/G)**")
        st.dataframe(
            top_ast[["PLAYER_NAME", "TEAM_NAME", "AST_PG", "GAMES_PLAYED"]],
            hide_index=True,
            use_container_width=True,
        )

    with col_reb:
        st.markdown("**Top Rebounders (REB/G)**")
        st.dataframe(
            top_reb[["PLAYER_NAME", "TEAM_NAME", "REB_PG", "GAMES_PLAYED"]],
            hide_index=True,
            use_container_width=True,
        )

    st.divider()

    # Chart – Points per game for top N
    st.subheader("📈 Points Per Game – Top 10")

    top10 = df.sort_values("PTS_PG", ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.barh(top10["PLAYER_NAME"], top10["PTS_PG"], color="orange")
    ax.invert_yaxis()
    ax.set_xlabel("Points per Game")
    ax.set_title(f"Top 10 Scorers — Season {season}")
    ax.grid(True, linestyle="--", alpha=0.4)
    st.pyplot(fig, use_container_width=True)

    st.caption("Source: Oracle 19c — table: " + source_table)
