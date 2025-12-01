import sys
import os

# Allow import of config.py from project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from config import get_connection


def render_team_view():
    """League standings + team trend from NBA_TEAM_STATS."""

    conn = get_connection()

    # Load seasons and teams
    seasons_df = pd.read_sql(
        "SELECT DISTINCT SEASON FROM NBA_TEAM_STATS ORDER BY SEASON DESC",
        conn,
    )
    if seasons_df.empty:
        st.error("No data found in NBA_TEAM_STATS.")
        conn.close()
        return

    seasons = seasons_df["SEASON"].tolist()

    # Season for league overview
    season_str = st.selectbox(
        "Season for league standings:",
        [str(s) for s in seasons],
        index=0,
        key="team_season_select",
    )
    season = int(season_str)

    # Load league data for that season
    league_df = pd.read_sql(
        """
        SELECT TEAM_NAME, SEASON, WINS, LOSSES, WIN_PCT, POINTS
        FROM NBA_TEAM_STATS
        WHERE SEASON = :season
        """,
        conn,
        params={"season": season},
    )

    if league_df.empty:
        st.warning(f"No league data for season {season}.")
        conn.close()
        return

    # Team selector for trend view (right side)
    teams = sorted(league_df["TEAM_NAME"].unique().tolist())
    team_name = st.selectbox(
        "Team to inspect (trend on right):",
        teams,
        index=0,
        key="trend_team_select",
    )

    # Load full history for that team
    team_history_df = pd.read_sql(
        """
        SELECT SEASON, WINS, LOSSES, WIN_PCT, POINTS
        FROM NBA_TEAM_STATS
        WHERE TEAM_NAME = :team_name
        ORDER BY SEASON
        """,
        conn,
        params={"team_name": team_name},
    )

    conn.close()

    # ---- League Overview (left) ----
    left_col, right_col = st.columns([1.3, 1])

    with left_col:
        st.subheader(f"🏁 League Standings — Season {season}")

        df = league_df.copy()
        df["GAMES"] = df["WINS"] + df["LOSSES"]
        df["WIN_PCT_PERCENT"] = (df["WIN_PCT"] * 100).round(2)

        # Summary metrics
        total_teams = len(df)
        best_row = df.sort_values("WIN_PCT", ascending=False).iloc[0]
        worst_row = df.sort_values("WIN_PCT", ascending=True).iloc[0]
        avg_win_pct = df["WIN_PCT_PERCENT"].mean()

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Teams", total_teams)
        m2.metric(
            "Best Win %",
            f"{best_row['WIN_PCT_PERCENT']:.2f}%",
            help=best_row["TEAM_NAME"],
        )
        m3.metric(
            "Worst Win %",
            f"{worst_row['WIN_PCT_PERCENT']:.2f}%",
            help=worst_row["TEAM_NAME"],
        )
        m4.metric("Avg League Win %", f"{avg_win_pct:.2f}%")

        # Standings table
        df_standings = df.copy()
        df_standings["RANK"] = (
            df_standings["WIN_PCT"].rank(ascending=False, method="dense").astype(int)
        )
        df_standings = df_standings.sort_values(["RANK", "TEAM_NAME"])

        df_standings = df_standings[
            [
                "RANK",
                "TEAM_NAME",
                "SEASON",
                "WINS",
                "LOSSES",
                "GAMES",
                "WIN_PCT_PERCENT",
                "POINTS",
            ]
        ].rename(
            columns={
                "RANK": "Rank",
                "TEAM_NAME": "Team",
                "SEASON": "Season",
                "WINS": "Wins",
                "LOSSES": "Losses",
                "GAMES": "Games",
                "WIN_PCT_PERCENT": "Win %",
                "POINTS": "Points",
            }
        )

        st.dataframe(df_standings, use_container_width=True, height=420)

        # Bar chart of win %
        fig, ax = plt.subplots(figsize=(10, max(4, len(df) * 0.35)))
        ax.barh(df["TEAM_NAME"], df["WIN_PCT_PERCENT"], color="mediumseagreen")
        ax.invert_yaxis()
        ax.set_xlabel("Win %")
        ax.set_title(f"Win % by Team — Season {season}")
        ax.grid(True, linestyle="--", alpha=0.4)
        st.pyplot(fig, use_container_width=True)

    # ---- Team Trend (right) ----
    with right_col:
        st.subheader(f"📈 {team_name} – Win % Over Seasons")

        if team_history_df.empty:
            st.info(f"No historical data available for {team_name}.")
        else:
            fig2, ax2 = plt.subplots(figsize=(8, 4))
            ax2.plot(
                team_history_df["SEASON"],
                team_history_df["WIN_PCT"] * 100,
                marker="o",
                color="royalblue",
                linewidth=3,
            )
            ax2.set_xlabel("Season")
            ax2.set_ylabel("Win %")
            ax2.set_title(f"{team_name} – Win % Trend")
            ax2.grid(True, linestyle="--", alpha=0.5)
            st.pyplot(fig2, use_container_width=True)
