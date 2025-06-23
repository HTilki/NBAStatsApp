"""
Season Stats Page
Displays league-wide season statistics.
"""

import streamlit as st
import polars as pl

from utils.connection import get_connection
from utils.app_state import AppState
from data.queries import get_season_stats, get_season_champion
from data.column_config import (
    PLAYER_SEASON_STATS_COLUMN_CONFIG,
    TEAM_SEASON_STATS_COLUMN_CONFIG,
)
from components.headers import page_header
from components.filters import season_filter, game_type_filter
from utils.data_processing import prepare_season_stats
from components.tables import stats_table
from components.charts import stat_bar_chart
from components.layout import tabbed_interface

# Initialize core state (teams, seasons)
AppState.initialize_core_state()

# Page header
page_header("Season Statistics")

# Add season selector
seasons = [season for season in st.session_state.get("seasons", [])]
selected_season = season_filter(seasons, default_index=0)

# Apply filters from sidebar
with st.sidebar:
    # Game type filter
    selected_game_type = game_type_filter(key_prefix="season_")

    # Stat type selection
    stat_types = {"team": "Team Stats", "player": "Player Stats"}

    selected_stat_type = st.selectbox(
        "Stat Type",
        options=list(stat_types.keys()),
        format_func=lambda x: stat_types[x],
        key="season_stat_type",
    )

    # Minimum games filter for players
    min_games = 0
    if selected_stat_type == "player":
        min_games = st.slider(
            "Minimum Games Played", min_value=0, max_value=120, value=30, step=1
        )

# Get data
conn = get_connection()
season_data = get_season_stats(
    conn, selected_season, selected_stat_type, selected_game_type
)

if not season_data.is_empty():
    # Process season stats data
    stats_data = prepare_season_stats(
        season_data, stat_type=selected_stat_type, min_games=min_games
    ).with_columns(
        # Round all int and float columns to 3 decimal place
        (pl.selectors.float()).round(4)
    )

    if stats_data.is_empty():
        st.warning("No data available for the selected filters.")
        st.stop()

    # Determine which columns to show
    if selected_stat_type == "team":
        column_config = TEAM_SEASON_STATS_COLUMN_CONFIG
        sort_column = "wins"
        group_name = "team"
    else:  # player stats
        column_config = PLAYER_SEASON_STATS_COLUMN_CONFIG
        sort_column = "ppg"
        group_name = "player"

    # Define tab functions
    def show_overview():
        # Message to inform the user about the sorting column
        st.info(
            f"Data is sorted by {sort_column} in descending order. Click on the column header to sort by a different column."
        )
        # Display overview table
        sorted_data = stats_data.sort(sort_column, descending=True, nulls_last=True)
        stats_table(sorted_data, column_config=column_config)

        # Add season champion
        if selected_stat_type == "team":
            champion = get_season_champion(conn, selected_season)
            if champion:
                st.success(f"NBA Champion: {champion['team_name']}", icon="🏆")
            else:
                st.warning("No NBA champion for this season yet.")

    def show_points():
        # Display points leaders
        points_data = stats_data.sort(
            "ppg", descending=True, nulls_last=True
        ).with_columns(pl.col("ppg").round(1).name.keep())
        stats_table(points_data, column_config=column_config)

        # Display chart
        pts_fig = stat_bar_chart(
            points_data.head(10),
            x_col=group_name,
            y_col="ppg",
            title=f"Top 10 Scoring {selected_stat_type.title()} ({selected_season})",
        )
        st.plotly_chart(pts_fig, use_container_width=True)

    def show_rebounds():
        # Display rebound leaders with offensive and defensive rebounds breakdown
        rebound_data = stats_data.sort(
            "rpg", descending=True, nulls_last=True
        ).with_columns(pl.col(["rpg", "orpg", "drpg"]).round(1).name.keep())
        stats_table(rebound_data, column_config=column_config)

        # Create columns for charts
        col1, col2 = st.columns(2)

        # Total rebounds chart
        with col1:
            rpg_fig = stat_bar_chart(
                rebound_data.head(10),
                x_col=group_name,
                y_col="rpg",
                title=f"Top 10 Total Rebounds ({selected_season})",
                labels={"rpg": "Total Rebounds"},
            )
            st.plotly_chart(rpg_fig, use_container_width=True)

        # Offensive vs Defensive rebounds comparison
        with col2:
            top10_rebounders = rebound_data.head(10)
            orpg_drpg_fig = stat_bar_chart(
                top10_rebounders,
                x_col=group_name,
                y_col=["orpg", "drpg"],
                title=f"ORB vs DRB Breakdown ({selected_season})",
                stack=True,
                labels={"orpg": "Offensive", "drpg": "Defensive"},
                colors=["#FF9B54", "#5DADE2"],
            )
            st.plotly_chart(orpg_drpg_fig, use_container_width=True)

        # Add explanation
        st.info(
            "Rebounding comparison shows both total rebounds (RPG) and the breakdown between offensive (ORPG) and defensive (DRPG) rebounds."
        )

    def show_assists():
        # Calculate assist to turnover ratio
        assist_data = (
            stats_data.with_columns(
                [
                    pl.col("apg").cast(pl.Float64).name.keep(),
                    pl.col("tpg").cast(pl.Float64).name.keep(),
                ]
            )
            .with_columns(
                (pl.col("apg") / pl.col("tpg")).round(2).alias("ast_to_ratio"),
            )
            .sort("apg", descending=True, nulls_last=True)
        )

        # Add assist-to-turnover ratio to column config
        extended_column_config = column_config.copy()
        extended_column_config["ast_to_ratio"] = st.column_config.NumberColumn(
            "AST/TO", format="%.2f", help="Assist to Turnover Ratio", width="small"
        )

        # Display assist leaders with AST/TO ratio
        stats_table(assist_data, column_config=extended_column_config)

        # Create columns for charts
        col1, col2 = st.columns(2)

        # Assists chart
        with col1:
            apg_fig = stat_bar_chart(
                assist_data.head(10),
                x_col=group_name,
                y_col="apg",
                title=f"Top 10 Assists Per Game ({selected_season})",
            )
            st.plotly_chart(apg_fig, use_container_width=True)

        # AST/TO ratio chart
        with col2:
            ratio_data = (
                assist_data.filter(pl.col("games_played") >= 10)
                .sort("ast_to_ratio", descending=True)
                .head(10)
            )
            ratio_fig = stat_bar_chart(
                ratio_data,
                x_col=group_name,
                y_col="ast_to_ratio",
                title=f"Top 10 AST/TO Ratio ({selected_season})",
                colors=["#27AE60"],
            )
            st.plotly_chart(ratio_fig, use_container_width=True)

        # Comparison chart - assists vs turnovers
        ast_tov_data = assist_data.head(10)
        ast_tov_fig = stat_bar_chart(
            ast_tov_data,
            x_col=group_name,
            y_col=["apg", "tpg"],
            title=f"Assists vs Turnovers ({selected_season})",
            stack=False,
            labels={"apg": "Assists", "tpg": "Turnovers"},
            colors=["#27AE60", "#E74C3C"],
        )
        st.plotly_chart(ast_tov_fig, use_container_width=True)

        # Add explanation
        st.info(
            "Assist to Turnover Ratio (AST/TO) measures playmaking efficiency. A higher ratio indicates better ball distribution with fewer mistakes."
        )

    def show_defense():
        # Set up sorting for defensive metrics based on stat type
        if selected_stat_type == "team":
            # For teams, sort by points allowed (ascending)
            defense_data = stats_data.sort("points_allowed", nulls_last=True)
            defense_metric = "points_allowed"
            defense_title = "Points Allowed Per Game"
            defense_color = "#8E44AD"  # Purple
            defense_label = "Points Allowed"
        else:
            # For players, sort by blocks (descending)
            defense_data = stats_data.sort("bpg", descending=True)
            defense_metric = "bpg"
            defense_title = "Blocks Per Game"
            defense_color = "#2471A3"  # Blue
            defense_label = "Blocks"

        # Display defense leaders table
        st.subheader(f"Defense Leaders - {selected_season}")
        stats_table(defense_data, column_config=column_config)

        # Create columns for charts
        col1, col2 = st.columns(2)

        # Primary defensive metric chart (points allowed or blocks)
        with col1:
            defense_fig = stat_bar_chart(
                defense_data.head(10),
                x_col=group_name,
                y_col=defense_metric,
                title=f"Top 10 {defense_title} ({selected_season})",
                colors=[defense_color],
                custom_hovertemplate=f"<b>%{{x}}</b><br>{defense_label}: %{{y:.1f}}<br>GP: %{{customdata[0]}}<extra></extra>",
                hover_data=["games_played"],
            )
            st.plotly_chart(defense_fig, use_container_width=True)

        # Blocks chart (if showing team data, otherwise show steals)
        with col2:
            if selected_stat_type == "team":
                # For teams, show blocks
                block_data = stats_data.sort("bpg", descending=True).head(10)
                block_fig = stat_bar_chart(
                    block_data,
                    x_col=group_name,
                    y_col="bpg",
                    title=f"Top 10 Blocking Teams ({selected_season})",
                    colors=["#148F77"],  # Teal
                    custom_hovertemplate="<b>%{x}</b><br>BPG: %{y:.1f}<br>GP: %{customdata[0]}<extra></extra>",
                    hover_data=["games_played"],
                )
                st.plotly_chart(block_fig, use_container_width=True)
            else:
                # For players, show steals
                steal_data = stats_data.sort("spg", descending=True).head(10)
                steal_fig = stat_bar_chart(
                    steal_data,
                    x_col=group_name,
                    y_col="spg",
                    title=f"Top 10 Steals Leaders ({selected_season})",
                    colors=["#D35400"],  # Orange
                    custom_hovertemplate="<b>%{x}</b><br>SPG: %{y:.1f}<br>GP: %{customdata[0]}<extra></extra>",
                    hover_data=["games_played"],
                )
                st.plotly_chart(steal_fig, use_container_width=True)

        # Defensive comparison chart
        if selected_stat_type == "players":
            # For players, compare blocks vs steals
            st.subheader("Defensive Stats Comparison")
            top_defenders = stats_data.sort(
                pl.col("bpg") + pl.col("spg"), descending=True
            ).head(10)
            defense_compare_fig = stat_bar_chart(
                top_defenders,
                x_col=group_name,
                y_col=["bpg", "spg"],
                title=f"Blocks vs Steals ({selected_season})",
                stack=False,
                labels={"bpg": "Blocks Per Game", "spg": "Steals Per Game"},
                colors=["#2471A3", "#D35400"],
                custom_hovertemplate="<b>%{x}</b><br>%{fullData.name}: %{y:.1f}<br>GP: %{customdata[0]}<extra></extra>",
                hover_data=["games_played"],
            )
            st.plotly_chart(defense_compare_fig, use_container_width=True)

        # Add explanation
        if selected_stat_type == "team":
            st.info(
                "Teams with lower points allowed per game typically have stronger defenses. "
                "Blocks can indicate rim protection ability, another key aspect of team defense."
            )
        else:
            st.info(
                "Blocks and steals are key defensive statistics for individual players. "
                "Elite defenders typically excel in one or both categories."
            )

    def show_shooting():
        def multi_shooting_comparison(shooting_column: str):
            # Multi-shooting comparison chart
            st.subheader("Shooting Efficiency Comparison")
            top_shooters = shooting_data.sort(
                shooting_column, descending=True, nulls_last=True
            ).head(8)

            # For the multi-metric chart, create a comprehensive hover template
            multi_hover_template = (
                "<b>%{x}</b><br>"
                + "%{fullData.name}: %{y:.1f}%<br>"
                + "GP: "
                + top_shooters["games_played"].cast(pl.Utf8)[0]
                + "<extra></extra>"
            )

            shooting_comparison = stat_bar_chart(
                top_shooters,
                x_col=group_name,
                y_col=[
                    "fg_pct",
                    "three_p_pct",
                    "two_p_pct",
                    "ft_pct",
                ],
                title=f"Shooting Efficiency Breakdown ({selected_season})",
                stack=False,
                labels={
                    "fg_pct": "FG%",
                    "three_p_pct": "3P%",
                    "two_p_pct": "2P%",
                    "ft_pct": "FT%",
                },
                colors=["#4A235A", "#1A5276", "#117A65", "#D35400"],
                hover_data=["games_played"],
                custom_hovertemplate=multi_hover_template,
            )
            return st.plotly_chart(shooting_comparison, use_container_width=True)

        # Compare different shooting stats (FG%, 3PT%, 2PT%, FT%)
        shooting_data = stats_data.filter(pl.col("fga") >= 5)

        # Create tabs for different shooting metrics
        shooting_tabs = st.tabs(
            ["Field Goal %", "Three-Point %", "Two-Point %", "Free Throw %"]
        )

        # Field Goal % Tab
        with shooting_tabs[0]:
            shooting_column = "fg_pct"
            fg_data = shooting_data.sort(shooting_column, descending=True)
            st.subheader("Field Goal Percentage Leaders")
            stats_table(fg_data, column_config=column_config)

            fg_fig = stat_bar_chart(
                fg_data.head(10),
                x_col=group_name,
                y_col=shooting_column,
                title=f"Top 10 FG% Leaders ({selected_season})",
                colors=["#4A235A"],
                hover_data=["fg", "fga", "games_played"],
                custom_hovertemplate="<b>%{x}</b><br>FG%: %{y:.1f}%<br>FGM: %{customdata[0]:.1f}<br>FGA: %{customdata[1]:.1f}<br>GP: %{customdata[2]}<extra></extra>",
            )
            st.plotly_chart(fg_fig, use_container_width=True)

            # Show multi-shooting comparison chart
            multi_shooting_comparison(shooting_column)

        # Three-Point % Tab
        with shooting_tabs[1]:
            shooting_column = "three_p_pct"
            three_p_data = shooting_data.filter(pl.col("three_pa") >= 1).sort(
                shooting_column, descending=True
            )
            st.subheader("Three-Point Percentage Leaders")
            stats_table(three_p_data, column_config=column_config)

            three_p_fig = stat_bar_chart(
                three_p_data.head(10),
                x_col=group_name,
                y_col=shooting_column,
                title=f"Top 10 3PT% Leaders ({selected_season})",
                colors=["#1A5276"],
                hover_data=["three_p", "three_pa", "games_played"],
                custom_hovertemplate="<b>%{x}</b><br>3P%: %{y:.1f}%<br>3PM: %{customdata[0]:.1f}<br>3PA: %{customdata[1]:.1f}<br>GP: %{customdata[2]}<extra></extra>",
            )
            st.plotly_chart(three_p_fig, use_container_width=True)

            # Show multi-shooting comparison chart
            multi_shooting_comparison(shooting_column)

        # Two-Point % Tab
        with shooting_tabs[2]:
            shooting_column = "two_p_pct"
            two_p_data = shooting_data.filter(pl.col("two_papg") >= 2).sort(
                shooting_column, descending=True
            )
            st.subheader("Two-Point Percentage Leaders")
            stats_table(two_p_data, column_config=column_config)

            two_p_fig = stat_bar_chart(
                two_p_data.head(10),
                x_col=group_name,
                y_col=shooting_column,
                title=f"Top 10 2PT% Leaders ({selected_season})",
                colors=["#117A65"],
                hover_data=["two_ppg", "two_papg", "games_played"],
                custom_hovertemplate="<b>%{x}</b><br>2P%: %{y:.1f}%<br>2PM: %{customdata[0]:.1f}<br>2PA: %{customdata[1]:.1f}<br>GP: %{customdata[2]}<extra></extra>",
            )
            st.plotly_chart(two_p_fig, use_container_width=True)

            # Show multi-shooting comparison chart
            multi_shooting_comparison(shooting_column)

        # Free Throw % Tab
        with shooting_tabs[3]:
            shooting_column = "ft_pct"
            ft_data = shooting_data.filter(pl.col("fta") >= 1).sort(
                shooting_column, descending=True
            )
            st.subheader("Free Throw Percentage Leaders")
            stats_table(ft_data, column_config=column_config)

            ft_fig = stat_bar_chart(
                ft_data.head(10),
                x_col=group_name,
                y_col=shooting_column,
                title=f"Top 10 FT% Leaders ({selected_season})",
                colors=["#D35400"],
                hover_data=["ft", "fta", "games_played"],
                custom_hovertemplate="<b>%{x}</b><br>FT%: %{y:.1f}%<br>FTM: %{customdata[0]:.1f}<br>FTA: %{customdata[1]:.1f}<br>GP: %{customdata[2]}<extra></extra>",
            )
            st.plotly_chart(ft_fig, use_container_width=True)

            # Show multi-shooting comparison chart
            multi_shooting_comparison(shooting_column)

    # Create tabbed interface
    tabbed_interface(
        {
            "Overview": show_overview,
            "Points": show_points,
            "Rebounds": show_rebounds,
            "Assists": show_assists,
            "Defense": show_defense,
            "Shooting": show_shooting,
        }
    )

else:
    st.warning(f"No data available for season {selected_season}.")
