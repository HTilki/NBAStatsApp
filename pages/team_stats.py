"""
Team Stats Page
Displays statistics for a selected team.
"""

import streamlit as st
import polars as pl

from utils.connection import get_connection
from data.queries import get_team_stats
from utils.app_state import AppState
from utils.team_processing import (
    prepare_team_data,
    prepare_team_game_log,
)
from utils.game_processing import filter_data_by_game_filters
from utils.data_processing import (
    get_team_overall_stats,
    get_team_season_stats,
    get_win_percentage_data,
    get_against_opponents_stats,
    get_shooting_stats,
)
from utils.stats_aggregation import (
    calculate_win_loss_record,
)
from data.column_config import (
    TEAM_STAT_AGG_COLUMN_CONFIG,
    TEAM_GAME_LOG_COLUMN_CONFIG,
    OPPONENT_STAT_AGG_COLUMN_CONFIG,
)
from components.headers import page_header, team_header
from components.filters import (
    game_type_filter,
    metric_selector,
    season_filter,
    opponent_filter,
)
from components.tables import stats_table
from components.charts import (
    win_percentage_chart,
    win_percentage_opponent_chart,
    # opponent_comparison_chart,
    team_performance_trend_chart,
    multi_metric_season_chart,
    player_shot_chart,
)
from components.layout import tabbed_interface

# Initialize core state (teams, seasons)
AppState.initialize_core_state()

# List of NBA teams
nba_teams = (
    pl.DataFrame(st.session_state["teams"]).select("abbreviation").to_series().to_list()
)
# Page header
page_header("Team Stats")

# Team selection dropdown
team_options = [""] + [team["name"] for team in st.session_state.get("teams", [])]

# Check if a team is selected from another page and set the selectbox default
default_selection = ""
if st.session_state.get("selected_team", ""):
    default_selection = st.session_state.get("selected_team")

selected_team = st.selectbox(
    "Select a Team",
    options=team_options,
    index=team_options.index(default_selection)
    if default_selection in team_options
    else 0,
)

# Clear the session state selected_team if user explicitly selects a different team
if selected_team != st.session_state.get("selected_team", ""):
    if selected_team == "":
        st.session_state["selected_team"] = ""
    else:
        st.session_state["selected_team"] = selected_team

# Use the selected team from selectbox as the primary source
if not selected_team:
    selected_team = ""


# Function to get team abbreviation from name
def get_team_abbreviation(team_name):
    for team in st.session_state.get("teams", []):
        if team["name"] == team_name:
            return team["abbreviation"]
    return None


# If a team is selected, get its data
if selected_team:
    team_abbreviation = get_team_abbreviation(selected_team)

    if team_abbreviation:
        # Get team data
        conn = get_connection()
        team_data_raw = get_team_stats(conn, team_abbreviation)
        conn.close()

        if not team_data_raw.is_empty():
            # Process team data
            team_data = prepare_team_data(team_data_raw)

            # Get unique opponents for filter
            unique_opponents = (
                team_data.filter(pl.col("opponent").is_in(nba_teams))
                .select("opponent")
                .unique("opponent")
                .sort("opponent", descending=False, maintain_order=True)
                .to_series()
                .to_list()
            )

            # Display team logo and name
            team_header(name=selected_team, team_abbreviation=team_abbreviation)

            # Sidebar filters

            # Season selector
            team_seasons = (
                team_data.select("season").unique().sort("season", descending=True)
            )
            season_options = ["All Seasons"] + team_seasons["season"].to_list()
            selected_season = season_filter(
                key_prefix="team_", seasons=season_options, sidebar=True
            )

            # Game type filter
            selected_game_type = game_type_filter(key_prefix="team_", sidebar=True)

            # Opponent filter
            selected_opponent = opponent_filter(
                opponents=unique_opponents, key_prefix="team_", sidebar=True
            )

            # Metric selector for charts
            selected_metric, metric_name, is_percentage = metric_selector(
                key_prefix="team_", sidebar=True
            )

            # Create filters dictionary
            filters = {
                "game_type": selected_game_type,
                "season": selected_season,
                "opponent": selected_opponent,
            }

            # Filter data using the filter_data_by_game_filters function
            filtered_data = filter_data_by_game_filters(team_data, filters)

            # Create separate filtered data for different views
            filtered_data_without_opponent = filter_data_by_game_filters(
                team_data, {k: v for k, v in filters.items() if k != "opponent"}
            )

            # Create separate filtered data for trends (without season filter)
            filtered_data_without_season = filter_data_by_game_filters(
                team_data, {k: v for k, v in filters.items() if k != "season"}
            )

            if filtered_data.is_empty():
                st.warning("No metrics available for the selected filters.")
                # st.stop()

            # Show content in tabs
            def show_team_overview():
                # Display team overview stats

                # Get team record
                record = calculate_win_loss_record(filtered_data)

                # Calculate basic team stats
                team_stats = get_team_overall_stats(filtered_data)

                team_seasons_data = get_team_season_stats(filtered_data)

                # Display team metrics
                if not team_stats.is_empty():
                    cols = st.columns(6)
                    with cols[0]:
                        st.metric("Record", f"{record['wins']}-{record['losses']}")
                    with cols[1]:
                        st.metric("PPG", f"{team_stats[0, 'ppg']:.1f}")
                    with cols[2]:
                        st.metric("RPG", f"{team_stats[0, 'rpg']:.1f}")
                    with cols[3]:
                        st.metric("APG", f"{team_stats[0, 'apg']:.1f}")
                    with cols[4]:
                        st.metric("FG%", f"{team_stats[0, 'fg_pct'] * 100:.1f}%")
                    with cols[5]:
                        st.metric("3P%", f"{team_stats[0, 'three_p_pct'] * 100:.1f}%")
                # Display team stats table
                if not team_seasons_data.is_empty():
                    with st.expander("Season Team Statistics", expanded=True):
                        stats_table(
                            team_seasons_data, column_config=TEAM_STAT_AGG_COLUMN_CONFIG
                        )

                # Prepare data for win percentage chart per location
                win_pct_data = get_win_percentage_data(filtered_data, selected_opponent)

                # Display win percentage chart
                if win_pct_data:
                    fig = win_percentage_chart(win_pct_data)
                    with st.expander("Win Percentage by Location", expanded=True):
                        st.plotly_chart(fig, use_container_width=True)

            def show_game_log():
                # Display game log
                game_log = prepare_team_game_log(filtered_data)
                stats_table(game_log, column_config=TEAM_GAME_LOG_COLUMN_CONFIG)

            def show_opponent_stats():
                # Display stats vs opponents
                opponent_stats = get_against_opponents_stats(
                    filtered_data_without_opponent
                ).filter(pl.col("opponent").is_in(nba_teams))

                # Show opponent win percentage chart
                if not opponent_stats.is_empty():
                    fig = win_percentage_opponent_chart(opponent_stats)
                    with st.expander("Win Percentage Against Opponents", expanded=True):
                        st.plotly_chart(fig, use_container_width=True)

                    # Show opponent stats table
                    with st.expander("Statistics Against Opponent", expanded=True):
                        stats_table(
                            opponent_stats,
                            column_config=OPPONENT_STAT_AGG_COLUMN_CONFIG,
                        )

                # Show opponent comparison chart
                # metrics_to_compare = ["ppg", "rpg", "apg", "fg_pct", "three_p_pct"]
                # metric_display_names = {
                #    "ppg": "Points Per Game",
                #    "rpg": "Rebounds Per Game",
                #    "apg": "Assists Per Game",
                #    "fg_pct": "Field Goal %",
                #    "three_p_pct": "3-Point %",
                # }
                # fig = opponent_comparison_chart(
                #    opponent_stats.sort("win_pct", descending=True).head(8),
                #    metrics_to_compare,
                #    metric_names=metric_display_names,
                # )
                # st.plotly_chart(fig, use_container_width=True)

            def show_trends():
                # Create season trend data
                season_trend = (
                    filtered_data_without_season.with_columns(
                        pl.when(pl.col("outcome") == 1)
                        .then(pl.lit(1))
                        .otherwise(pl.lit(0))
                        .alias("wins"),
                        pl.when(pl.col("outcome") == 0)
                        .then(pl.lit(1))
                        .otherwise(pl.lit(0))
                        .alias("losses"),
                    )
                    .group_by(["season", "team"])
                    .agg(
                        pl.len().alias("games_played"),
                        pl.mean("points").round(1).alias("ppg"),
                        pl.mean("assists").round(1).alias("apg"),
                        pl.mean("rebounds").round(1).alias("rpg"),
                        pl.mean("offensive_rebounds").round(1).alias("orpg"),
                        pl.mean("defensive_rebounds").round(1).alias("drpg"),
                        pl.mean("steals").round(1).alias("spg"),
                        pl.mean("blocks").round(1).alias("bpg"),
                        pl.mean("field_goal_percent").mul(100).round(1).alias("fg_pct"),
                        pl.mean("three_point_percent")
                        .mul(100)
                        .round(1)
                        .alias("three_p_pct"),
                        pl.mean("attempted_three_point").round(1).alias("three_pa"),
                        pl.sum("wins").alias("wins"),
                        pl.sum("losses").alias("losses"),
                    )
                    .with_columns(
                        (pl.col("wins") / (pl.col("wins") + pl.col("losses"))).alias(
                            "win_percentage"
                        )
                    )
                    .sort("season")
                )
                if not season_trend.is_empty():
                    # Display basic stats trend
                    with st.expander("Basic Statistics by Season", expanded=True):
                        basic_stats = [
                            "ppg",
                            "apg",
                            "rpg",
                            "orpg",
                            "drpg",
                            "spg",
                            "bpg",
                        ]
                        basic_stat_names = {
                            "ppg": "PPG",
                            "apg": "APG",
                            "rpg": "RPG",
                            "orpg": "ORPG",
                            "drpg": "DRPG",
                            "spg": "SPG",
                            "bpg": "BPG",
                        }

                        fig = multi_metric_season_chart(
                            season_trend, basic_stats, metric_names=basic_stat_names
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    # Display shooting stats trend
                    with st.expander("Shooting Statistics by Season", expanded=True):
                        # Define shooting stat options
                        shooting_stats_options = [
                            "Field Goals",
                            "2-Point Shots",
                            "3-Point Shots",
                            "Free Throws",
                        ]

                        # User selection
                        shooting_stats_selected = st.multiselect(
                            "Select Shooting Stats to Display",
                            options=shooting_stats_options,
                            default=shooting_stats_options,
                        )

                        # Generate shooting stats data based on selection
                        if shooting_stats_selected:
                            shooting_data = get_shooting_stats(
                                filtered_data_without_season
                            )

                            fig = player_shot_chart(
                                shooting_data, shooting_stats_selected
                            )
                            if fig:
                                st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info(
                                "Please select at least one shooting statistic type to display"
                            )

                    # Display win percentage trend
                    with st.expander("Win Percentage by Season", expanded=True):
                        fig = team_performance_trend_chart(
                            season_trend,
                            metric="win_percentage",
                            y_label="Win Percentage",
                            format_as_percent=True,
                        )
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(
                        "No season trend data available for the selected filters."
                    )

            # Create tabbed interface
            tabbed_interface(
                {
                    "Team Overview": show_team_overview,
                    "Game Log": show_game_log,
                    "Opponent Stats": show_opponent_stats,
                    "Trends": show_trends,
                }
            )

        else:
            st.warning(f"No data found for team '{selected_team}'.")
    else:
        st.error(f"Could not find abbreviation for team '{selected_team}'.")
else:
    st.info("Select a team from the dropdown or navigate from another page.")
