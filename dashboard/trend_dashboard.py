import sys
import os

# Make sure we can import config.py from project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from config import get_connection

# ---------------------------------
# Team Logos (ESPN URLs)
# ---------------------------------
team_logos = {
    "Atlanta Hawks": "https://a.espncdn.com/i/teamlogos/nba/500/atl.png",
    "Boston Celtics": "https://a.espncdn.com/i/teamlogos/nba/500/bos.png",
    "Brooklyn Nets": "https://a.espncdn.com/i/teamlogos/nba/500/bkn.png",
    "Charlotte Hornets": "https://a.espncdn.com/i/teamlogos/nba/500/cha.png",
    "Chicago Bulls": "https://a.espncdn.com/i/teamlogos/nba/500/chi.png",
    "Cleveland Cavaliers": "https://a.espncdn.com/i/teamlogos/nba/500/cle.png",
    "Dallas Mavericks": "https://a.espncdn.com/i/teamlogos/nba/500/dal.png",
    "Denver Nuggets": "https://a.espncdn.com/i/teamlogos/nba/500/den.png",
    "Detroit Pistons": "https://a.espncdn.com/i/teamlogos/nba/500/det.png",
    "Golden State Warriors": "https://a.espncdn.com/i/teamlogos/nba/500/gs.png",
    "Houston Rockets": "https://a.espncdn.com/i/teamlogos/nba/500/hou.png",
    "Indiana Pacers": "https://a.espncdn.com/i/teamlogos/nba/500/ind.png",
    "LA Clippers": "https://a.espncdn.com/i/teamlogos/nba/500/lac.png",
    "Los Angeles Lakers": "https://a.espncdn.com/i/teamlogos/nba/500/lal.png",
    "Memphis Grizzlies": "https://a.espncdn.com/i/teamlogos/nba/500/mem.png",
    "Miami Heat": "https://a.espncdn.com/i/teamlogos/nba/500/mia.png",
    "Milwaukee Bucks": "https://a.espncdn.com/i/teamlogos/nba/500/mil.png",
    "Minnesota Timberwolves": "https://a.espncdn.com/i/teamlogos/nba/500/min.png",
    "New Orleans Pelicans": "https://a.espncdn.com/i/teamlogos/nba/500/no.png",
    "New York Knicks": "https://a.espncdn.com/i/teamlogos/nba/500/ny.png",
    "Oklahoma City Thunder": "https://a.espncdn.com/i/teamlogos/nba/500/okc.png",
    "Orlando Magic": "https://a.espncdn.com/i/teamlogos/nba/500/orl.png",
    "Philadelphia 76ers": "https://a.espncdn.com/i/teamlogos/nba/500/phi.png",
    "Phoenix Suns": "https://a.espncdn.com/i/teamlogos/nba/500/phx.png",
    "Portland Trail Blazers": "https://a.espncdn.com/i/teamlogos/nba/500/por.png",
    "Sacramento Kings": "https://a.espncdn.com/i/teamlogos/nba/500/sac.png",
    "San Antonio Spurs": "https://a.espncdn.com/i/teamlogos/nba/500/sa.png",
    "Toronto Raptors": "https://a.espncdn.com/i/teamlogos/nba/500/tor.png",
    "Utah Jazz": "https://a.espncdn.com/i/teamlogos/nba/500/utah.png",
    "Washington Wizards": "https://a.espncdn.com/i/teamlogos/nba/500/wsh.png"
}

# ---------------------------------
# Modern teams list + helper
# ---------------------------------
MODERN_TEAMS = [
    "Atlanta Hawks", "Boston Celtics", "Brooklyn Nets", "Charlotte Hornets",
    "Chicago Bulls", "Cleveland Cavaliers", "Dallas Mavericks", "Denver Nuggets",
    "Detroit Pistons", "Golden State Warriors", "Houston Rockets", "Indiana Pacers",
    "LA Clippers", "Los Angeles Lakers", "Memphis Grizzlies", "Miami Heat",
    "Milwaukee Bucks", "Minnesota Timberwolves", "New Orleans Pelicans",
    "New York Knicks", "Oklahoma City Thunder", "Orlando Magic",
    "Philadelphia 76ers", "Phoenix Suns", "Portland Trail Blazers",
    "Sacramento Kings", "San Antonio Spurs", "Toronto Raptors",
    "Utah Jazz", "Washington Wizards"
]


def filter_modern_teams(df):
    """Return only rows where TEAM_NAME is a modern NBA franchise."""
    if "TEAM_NAME" not in df.columns:
        return df
    return df[df["TEAM_NAME"].isin(MODERN_TEAMS)]


# ---------------------------------
# Streamlit Page Setup
# ---------------------------------
st.set_page_config(
    page_title="NBA Team Trends",
    page_icon="🏀",
    layout="wide"
)

st.title("🏀 NBA Team Trends Dashboard")
st.caption("Powered by Oracle 19c + Python + Streamlit")


# ---------------------------------
# Connect to Oracle
# ---------------------------------
try:
    conn = get_connection()
except Exception as e:
    st.error(f"Database connection failed: {e}")
    st.stop()

# ---------------------------------
# Load Teams & Seasons (for filters)
# ---------------------------------
teams_df = pd.read_sql(
    "SELECT DISTINCT TEAM_NAME FROM NBA_TEAM_STATS ORDER BY TEAM_NAME",
    conn
)
teams = teams_df["TEAM_NAME"].tolist()

seasons_df = pd.read_sql(
    "SELECT DISTINCT SEASON FROM NBA_TEAM_STATS ORDER BY SEASON DESC",
    conn
)
seasons = seasons_df["SEASON"].tolist()

if not teams or not seasons:
    st.error("No data found in NBA_TEAM_STATS. Check your ETL or table.")
    conn.close()
    st.stop()

# ---------------------------------
# Sidebar Filters
# ---------------------------------
with st.sidebar:
    st.header("Filters")

    # Season for league-wide overview / standings
    season_overview = st.selectbox(
        "Season for League Overview:",
        [str(s) for s in seasons],
        index=0
    )

    # Team-level filters
    team_name = st.selectbox("Team for detailed view:", teams, index=0)

    season_filter = st.selectbox(
        "Team Season Filter:",
        ["All Seasons"] + [str(s) for s in seasons],
        index=0
    )

    modern_only = st.checkbox("Show modern NBA teams only (where applicable)", value=True)

# Show team logo (if available)
if team_name in team_logos:
    st.image(team_logos[team_name], width=120)

# ---------------------------------
# Load League Data for Selected Season
# ---------------------------------
df_league = pd.read_sql(
    """
    SELECT TEAM_NAME, SEASON, WINS, LOSSES, WIN_PCT, POINTS
    FROM NBA_TEAM_STATS
    WHERE SEASON = :season
    ORDER BY WIN_PCT DESC
    """,
    conn,
    params={"season": int(season_overview)}
)

league_df = df_league.copy()
if modern_only:
    league_df = filter_modern_teams(league_df)

# ---------------------------------
# Load Team Data (All Seasons for that team)
# ---------------------------------
df_team_all = pd.read_sql(
    """
    SELECT SEASON, WINS, LOSSES, WIN_PCT, POINTS
    FROM NBA_TEAM_STATS
    WHERE TEAM_NAME = :team_name
    ORDER BY SEASON
    """,
    conn,
    params={"team_name": team_name}
)

if df_team_all.empty:
    st.warning(f"No data found for {team_name}.")
    conn.close()
    st.stop()

# Apply team filter
if season_filter == "All Seasons":
    df_filtered = df_team_all.copy()
else:
    df_filtered = df_team_all[df_team_all["SEASON"] == int(season_filter)]

if df_filtered.empty:
    st.warning(f"No data for {team_name} in season {season_filter}.")
    conn.close()
    st.stop()

# ---------------------------------
# Summary for Current Team View
# ---------------------------------
st.markdown("### 📊 Current Team View Summary")
st.markdown(
    f"""
    **Team:** {team_name}  
    **Team Season Filter:** {season_filter}  
    **Records Found:** {len(df_filtered)}  
    """
)
st.divider()

# ---------------------------------
# Performance Metrics (Filtered Team View)
# ---------------------------------
avg_win_pct = (df_filtered["WIN_PCT"].mean() or 0) * 100
total_wins = int(df_filtered["WINS"].sum())
total_losses = int(df_filtered["LOSSES"].sum())
total_points = int(df_filtered["POINTS"].sum())

st.markdown("### 🏆 Team Performance Metrics (Current Filter)")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Average Win %", f"{avg_win_pct:.2f}%")
c2.metric("Total Wins", total_wins)
c3.metric("Total Losses", total_losses)
c4.metric("Total Points", total_points)

st.divider()

# ---------------------------------
# Tabs Layout
# ---------------------------------
tab_overview, tab_trend, tab_wl, tab_top10, tab_players, tab_games = st.tabs(
    [
        "📋 Team Overview (League)",
        "📈 Team Win % Trend",
        "🏀 Wins vs Losses",
        "🏆 Top 10 Team Seasons",
        "👤 Player Overview",
        "📓 Game Logs"
    ]
)

# ---------------------------------
# 📋 TAB 1: TEAM OVERVIEW (LEAGUE / STANDINGS)
# ---------------------------------
with tab_overview:
    st.subheader(f"📋 League Overview — Season {season_overview}")

    if league_df.empty:
        st.warning(
            "No league data available for this season with the current filter. "
            "Try unticking 'Show modern NBA teams only'."
        )
    else:
        df_league_display = league_df.copy()
        df_league_display["WIN_PCT_PERCENT"] = (df_league_display["WIN_PCT"] * 100).round(2)
        df_league_display["GAMES"] = df_league_display["WINS"] + df_league_display["LOSSES"]

        # Summary metrics
        total_teams = len(df_league_display)
        best_row = df_league_display.sort_values("WIN_PCT", ascending=False).iloc[0]
        worst_row = df_league_display.sort_values("WIN_PCT", ascending=True).iloc[0]
        avg_win_pct_league = df_league_display["WIN_PCT_PERCENT"].mean()
        max_points = df_league_display["POINTS"].max()

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Teams in View", total_teams)
        m2.metric("Best Win %", f"{best_row['WIN_PCT_PERCENT']:.2f}% ({best_row['TEAM_NAME']})")
        m3.metric("Worst Win %", f"{worst_row['WIN_PCT_PERCENT']:.2f}% ({worst_row['TEAM_NAME']})")
        m4.metric("Max Points (Season)", int(max_points))

        st.markdown("### 🏁 Standings (Ranked by Win %)")

        df_standings = df_league_display.copy()
        df_standings["RANK"] = df_standings["WIN_PCT"].rank(
            ascending=False, method="dense"
        ).astype(int)
        df_standings = df_standings.sort_values(["RANK", "TEAM_NAME"])

        display_cols = [
            "RANK", "TEAM_NAME", "SEASON",
            "WINS", "LOSSES", "GAMES",
            "WIN_PCT_PERCENT", "POINTS"
        ]
        df_standings = df_standings[display_cols]
        df_standings = df_standings.rename(
            columns={
                "RANK": "Rank",
                "TEAM_NAME": "Team",
                "SEASON": "Season",
                "WINS": "Wins",
                "LOSSES": "Losses",
                "GAMES": "Games",
                "WIN_PCT_PERCENT": "Win %",
                "POINTS": "Points"
            }
        )

        st.dataframe(df_standings, use_container_width=True)

        st.markdown("### 📊 Win % by Team (Bar Chart)")

        # Dynamic height based on number of teams
        num_teams = len(df_league_display)
        fig_height = max(4, min(12, num_teams * 0.35))

        fig1, ax1 = plt.subplots(figsize=(12, fig_height))
        ax1.barh(df_league_display["TEAM_NAME"], df_league_display["WIN_PCT_PERCENT"], color="mediumseagreen")
        ax1.invert_yaxis()
        ax1.set_xlabel("Win %")
        ax1.set_title(f"Win % by Team — Season {season_overview}")
        ax1.grid(True, linestyle="--", alpha=0.4)
        st.pyplot(fig1, use_container_width=True)

# ---------------------------------
# 📈 TAB 2: TEAM WIN % TREND (PER TEAM)
# ---------------------------------
with tab_trend:
    st.subheader(f"📈 Win % Trend — {team_name}")

    if season_filter != "All Seasons":
        st.caption(f"Filtered to season: {season_filter}")
    else:
        st.caption("Showing all seasons for selected team")

    fig2, ax2 = plt.subplots(figsize=(10, 5))
    ax2.plot(
        df_filtered["SEASON"],
        df_filtered["WIN_PCT"] * 100,
        marker="o",
        color="royalblue",
        linewidth=3
    )
    ax2.set_xlabel("Season")
    ax2.set_ylabel("Win %")
    ax2.set_title(f"{team_name} — Win % Over Seasons")
    ax2.grid(True, linestyle="--", alpha=0.5)
    st.pyplot(fig2, use_container_width=True)

# ---------------------------------
# 🏀 TAB 3: WINS VS LOSSES (SAMPLE OF TEAMS)
# ---------------------------------
with tab_wl:
    st.subheader("🏀 Wins vs Losses — Sample of Team Seasons")

    df_wl = pd.read_sql(
        """
        SELECT TEAM_NAME, SEASON, WINS, LOSSES
        FROM NBA_TEAM_STATS
        FETCH FIRST 40 ROWS ONLY
        """,
        conn
    )

    if modern_only:
        df_wl = filter_modern_teams(df_wl)

    if df_wl.empty:
        st.warning("No data available for Wins vs Losses with current filter.")
    else:
        fig3, ax3 = plt.subplots(figsize=(10, 5))
        ax3.scatter(
            df_wl["WINS"],
            df_wl["LOSSES"],
            color="orange",
            edgecolors="black",
            s=80
        )
        for _, row in df_wl.iterrows():
            ax3.text(
                row["WINS"] + 0.2,
                row["LOSSES"] + 0.2,
                row["TEAM_NAME"],
                fontsize=8
            )
        ax3.set_xlabel("Wins")
        ax3.set_ylabel("Losses")
        ax3.set_title("Wins vs Losses (Sample of Team Seasons)")
        ax3.grid(True, linestyle="--", alpha=0.5)
        st.pyplot(fig3, use_container_width=True)

# ---------------------------------
# 🏆 TAB 4: TOP 10 TEAM SEASONS BY WIN %
# ---------------------------------
with tab_top10:
    st.subheader("🏆 Top 10 Team Seasons by Win %")

    df_top10 = pd.read_sql(
        """
        SELECT TEAM_NAME, SEASON, WIN_PCT
        FROM NBA_TEAM_STATS
        ORDER BY WIN_PCT DESC
        FETCH FIRST 10 ROWS ONLY
        """,
        conn
    )

    if modern_only:
        df_top10 = filter_modern_teams(df_top10)

    if df_top10.empty:
        st.warning("No data available for Top 10 team seasons with current filter.")
    else:
        df_top10 = df_top10.copy()
        df_top10["WIN_PCT_PERCENT"] = (df_top10["WIN_PCT"] * 100).round(2)

        fig4, ax4 = plt.subplots(figsize=(10, 5))
        labels = [
            f"{t} ({int(s)})"
            for t, s in zip(df_top10["TEAM_NAME"], df_top10["SEASON"])
        ]
        ax4.barh(labels, df_top10["WIN_PCT_PERCENT"], color="mediumseagreen")
        ax4.invert_yaxis()
        ax4.set_xlabel("Win %")
        ax4.set_title("Top 10 Team Seasons by Win %")
        ax4.grid(True, linestyle="--", alpha=0.5)
        st.pyplot(fig4, use_container_width=True)

        st.markdown("### 📋 Top 10 Table")
        df_top10_table = df_top10.rename(
            columns={
                "TEAM_NAME": "Team",
                "SEASON": "Season",
                "WIN_PCT_PERCENT": "Win %"
            }
        )[["Team", "Season", "Win %"]]
        st.dataframe(df_top10_table, use_container_width=True)

# ---------------------------------
# 👤 TAB 5: PLAYER OVERVIEW (LIVE + FALLBACK)
# ---------------------------------
with tab_players:
    st.subheader("👤 Player Overview (Live Stats from API)")

    # Try live stats table first
    try:
        df_live = pd.read_sql(
            """
            SELECT PLAYER_ID, PLAYER_NAME, TEAM_NAME, SEASON, GAME_DATE,
                   POINTS, REBOUNDS, ASSISTS, STEALS, BLOCKS,
                   TURNOVERS, MINUTES, FG_PERCENT, THREE_PERCENT, FT_PERCENT
            FROM NBA_PLAYER_LIVE_STATS
            """,
            conn
        )
    except Exception:
        df_live = pd.DataFrame()

    if not df_live.empty:
        df_live["GAME_DATE"] = pd.to_datetime(df_live["GAME_DATE"])

        st.success("Using live player data from NBA_PLAYER_LIVE_STATS")

        players = sorted(df_live["PLAYER_NAME"].unique().tolist())
        sel_player = st.selectbox("Select a player:", players, index=0)

        seasons_live = sorted(df_live["SEASON"].dropna().unique().tolist())
        sel_season = st.selectbox(
            "Season:",
            ["All Seasons"] + [str(s) for s in seasons_live],
            index=0
        )

        df_p = df_live[df_live["PLAYER_NAME"] == sel_player].copy()
        if sel_season != "All Seasons":
            df_p = df_p[df_p["SEASON"] == int(sel_season)]

        if df_p.empty:
            st.warning("No stats for that filter yet.")
        else:
            avg_pts = df_p["POINTS"].mean() or 0
            avg_ast = df_p["ASSISTS"].mean() or 0
            avg_reb = df_p["REBOUNDS"].mean() or 0

            c1, c2, c3 = st.columns(3)
            c1.metric("Avg Points", f"{avg_pts:.1f}")
            c2.metric("Avg Assists", f"{avg_ast:.1f}")
            c3.metric("Avg Rebounds", f"{avg_reb:.1f}")

            st.markdown("#### 📈 Points by Game")
            df_p_sorted = df_p.sort_values("GAME_DATE")
            figp, axp = plt.subplots(figsize=(10, 4))
            axp.plot(df_p_sorted["GAME_DATE"], df_p_sorted["POINTS"], marker="o", color="royalblue")
            axp.set_xlabel("Game Date")
            axp.set_ylabel("Points")
            axp.grid(True, linestyle="--", alpha=0.5)
            st.pyplot(figp, use_container_width=True)

            st.markdown("#### 📝 Recent Games")
            show_cols = [
                "GAME_DATE", "TEAM_NAME", "SEASON",
                "POINTS", "ASSISTS", "REBOUNDS",
                "STEALS", "BLOCKS", "TURNOVERS", "MINUTES"
            ]
            st.dataframe(
                df_p_sorted[show_cols].tail(15),
                use_container_width=True
            )

    else:
        # fallback: static player stats table if live one is empty
        try:
            df_static = pd.read_sql(
                """
                SELECT PLAYER_NAME, TEAM_NAME, SEASON,
                       POINTS, ASSISTS, REBOUNDS,
                       STEALS, BLOCKS, TURNOVERS,
                       FG_PERCENT, THREE_PERCENT, FT_PERCENT
                FROM NBA_PLAYER_STATS
                """,
                conn
            )
        except Exception:
            df_static = pd.DataFrame()

        if df_static.empty:
            st.info(
                "No player stats available yet. "
                "Once you load NBA_PLAYER_LIVE_STATS (and/or NBA_PLAYER_STATS), "
                "this tab will show player-level analytics."
            )
        else:
            st.warning("Live table NBA_PLAYER_LIVE_STATS is empty — using NBA_PLAYER_STATS instead.")
            players = sorted(df_static["PLAYER_NAME"].unique().tolist())
            sel_player = st.selectbox("Select a player:", players, index=0)

            seasons_pl = sorted(df_static["SEASON"].dropna().unique().tolist())
            sel_season = st.selectbox(
                "Season:",
                ["All Seasons"] + [str(s) for s in seasons_pl],
                index=0
            )

            df_p = df_static[df_static["PLAYER_NAME"] == sel_player].copy()
            if sel_season != "All Seasons":
                df_p = df_p[df_p["SEASON"] == int(sel_season)]

            if df_p.empty:
                st.warning("No stats for that filter yet.")
            else:
                avg_pts = df_p["POINTS"].mean() or 0
                avg_ast = df_p["ASSISTS"].mean() or 0
                avg_reb = df_p["REBOUNDS"].mean() or 0

                c1, c2, c3 = st.columns(3)
                c1.metric("Avg Points", f"{avg_pts:.1f}")
                c2.metric("Avg Assists", f"{avg_ast:.1f}")
                c3.metric("Avg Rebounds", f"{avg_reb:.1f}")

                st.markdown("#### 🧾 Player Season Rows")
                st.dataframe(df_p, use_container_width=True)

# ---------------------------------
# 📓 TAB 6: GAME LOGS (NBA_GAME_LOGS)
# ---------------------------------
with tab_games:
    st.subheader("📓 Game Logs (From NBA_GAME_LOGS)")

    try:
        df_games = pd.read_sql(
            """
            SELECT GAME_DATE, SEASON, HOME_TEAM, AWAY_TEAM,
                   HOME_POINTS, AWAY_POINTS, WINNER, LOSER,
                   HOME_STREAK, AWAY_STREAK, NOTES
            FROM NBA_GAME_LOGS
            ORDER BY GAME_DATE
            """,
            conn
        )
    except Exception:
        df_games = pd.DataFrame()

    if df_games.empty:
        st.info("No records found in NBA_GAME_LOGS yet. Load your CSV game logs to see data here.")
    else:
        df_games["GAME_DATE"] = pd.to_datetime(df_games["GAME_DATE"])

        seasons_g = sorted(df_games["SEASON"].dropna().unique().tolist())
        season_sel = st.selectbox(
            "Season:",
            ["All Seasons"] + [str(s) for s in seasons_g],
            index=0
        )

        # Team filter from both home + away
        all_teams_g = sorted(
            set(df_games["HOME_TEAM"].unique().tolist())
            | set(df_games["AWAY_TEAM"].unique().tolist())
        )
        team_sel = st.selectbox(
            "Filter by team (home or away):",
            ["All Teams"] + all_teams_g,
            index=0
        )

        df_g = df_games.copy()
        if season_sel != "All Seasons":
            df_g = df_g[df_g["SEASON"] == int(season_sel)]

        if team_sel != "All Teams":
            df_g = df_g[
                (df_g["HOME_TEAM"] == team_sel) |
                (df_g["AWAY_TEAM"] == team_sel)
            ]

        if df_g.empty:
            st.warning("No games match your filters.")
        else:
            st.markdown("#### 🧾 Recent Games")
            st.dataframe(
                df_g.sort_values("GAME_DATE", ascending=False).head(30),
                use_container_width=True
            )

            st.markdown("#### 🏠 Home vs Away Points (Filtered Sample)")
            figg, axg = plt.subplots(figsize=(10, 4))
            axg.scatter(df_g["HOME_POINTS"], df_g["AWAY_POINTS"], color="purple", alpha=0.6)
            axg.set_xlabel("Home Points")
            axg.set_ylabel("Away Points")
            axg.set_title("Home vs Away Points (Filtered Games)")
            axg.grid(True, linestyle="--", alpha=0.4)
            st.pyplot(figg, use_container_width=True)

# ---------------------------------
# Close DB connection
# ---------------------------------
conn.close()
