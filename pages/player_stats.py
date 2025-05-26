"""
Player Profile Page
Displays statistics for a selected player.
"""

import streamlit as st
import polars as pl

from utils.connection import get_connection
from data.queries import get_player_stats
from data.column_config import (
    PLAYER_GAME_LOG_COLUMN_CONFIG,
    PLAYER_STAT_AGG_COLUMN_CONFIG,
)
from utils.app_state import AppState
from components.headers import page_header, player_header
from components.filters import (
    player_search_filter,
    game_type_filter,
    metric_selector,
    season_filter,
    opponent_filter,
)
from utils.player_processing import (
    prepare_player_data,
    prepare_player_season_stats,
    prepare_player_career_stats,
)
from utils.data_processing import (
    get_totals_metrics,
    get_highs_metrics,
    get_shooting_stats,
    get_away_home_split_df,
)
from utils.game_processing import filter_data_by_game_filters
from components.tables import stats_table
from components.charts import (
    season_metric_chart,
    career_metric_chart,
    player_shot_chart,
    location_bar_chart,
)
from components.layout import tabbed_interface, two_column_layout
from components.game_cards import totals_card, highs_card

# Initialize core state (teams, seasons)
AppState.initialize_core_state()

# Page header
page_header("Player Stats")

# Player search functionality
player_name = player_search_filter("Search for a player")

# Check if a player is selected from another page
selected_player = st.session_state.get("selected_player", "")
if selected_player:
    player_name = selected_player

# Search for player if name is provided
if player_name:
    # Get player data
    conn = get_connection()
    player_data_raw = get_player_stats(conn, player_name)
    conn.close()

    if not player_data_raw.is_empty():
        # Update player name with exact match from database
        player_name = player_data_raw[0, "player_name"]

        # Process player data
        player_data = prepare_player_data(player_data_raw)

        # Get unique opponents for filter
        unique_opponents = (
            player_data.select("opponent")
            .unique("opponent")
            .sort("opponent", descending=False, maintain_order=True)
            .to_series()
            .to_list()
        )

        # Get available seasons for this player
        player_seasons = (
            player_data.select("season").unique().sort("season", descending=True)
        )
        season_options = ["All Seasons"] + player_seasons["season"].to_list()

        # Display player photo and name header
        player_header(
            name=player_name,
            player_id=st.session_state.get("selected_player_id")
            or player_data_raw.item(0, "nba_player_id"),
        )

        # Sidebar filters

        # Season filter
        selected_season = season_filter(
            seasons=season_options, default_index=1, key_prefix="player_", sidebar=True
        )

        # Game type filter (Regular Season, Playoffs, etc.)
        selected_game_type = game_type_filter(key_prefix="player_", sidebar=True)

        # Team comparison filter
        selected_opponent = opponent_filter(
            opponents=unique_opponents,
            key_prefix="player_",
            sidebar=True,
        )

        # Metric selector for charts
        selected_metric, metric_name, is_percentage = metric_selector(
            key_prefix="player_", sidebar=True
        )

        # Create filters dictionary
        filters = {
            "game_type": selected_game_type,
            "season": selected_season,
            "opponent": selected_opponent,
        }

        # Filter data using the filter_data_by_game_filters function
        filtered_data = filter_data_by_game_filters(player_data, filters)

        # Create separate filtered data for opponent comparisons if needed
        filtered_data_without_opponent = filter_data_by_game_filters(
            player_data, {k: v for k, v in filters.items() if k != "opponent"}
        )
        # Create separate filtered data for opponent comparisons if needed
        filtered_data_without_season = filter_data_by_game_filters(
            player_data, {k: v for k, v in filters.items() if k != "season"}
        )

        # Show content in tabs
        def show_global_stats():
            if filtered_data_without_season.is_empty():
                st.info("No data available for the selected filters.")
                return
            # Prepare career stats
            career_stats, career_stats_mean, record = prepare_player_career_stats(
                filtered_data_without_season
            )
            season_stats, season_stats_mean, record = prepare_player_career_stats(
                filtered_data
            )

            # Display career stats summary metrics
            if not career_stats.is_empty():
                cols = st.columns(6)

                with cols[0]:
                    st.metric("PPG", f"{season_stats_mean.item(0, column='ppg'):.1f}")
                with cols[1]:
                    st.metric("RPG", f"{season_stats_mean[0, 'rpg']:.1f}")
                with cols[2]:
                    st.metric("APG", f"{season_stats_mean[0, 'apg']:.1f}")
                with cols[3]:
                    st.metric("FG%", f"{(season_stats_mean[0, 'fg_pct']):.1f}%")
                with cols[5]:
                    st.metric("Record", f"{record['wins']}-{record['losses']}")

                with st.expander("Season Stats", expanded=True):
                    stats_table(
                        career_stats, column_config=PLAYER_STAT_AGG_COLUMN_CONFIG
                    )

                # Display career stats mean in expander
                with st.expander("Global Career Stats", expanded=False):
                    stats_table(
                        career_stats_mean, column_config=PLAYER_STAT_AGG_COLUMN_CONFIG
                    )

        def show_season_graphs():
            if filtered_data.is_empty():
                st.info("No data available for the selected filters.")
                return

            # Summary stats card
            def season_stats_card():
                with st.expander("Season Totals", expanded=True):
                    # Display season totals card
                    totals_card(
                        *get_totals_metrics(filtered_data_without_opponent),
                    )

                # Career highs against selected team
                with st.expander("Season Highs", expanded=True):
                    # Get season highs
                    highs_card(
                        *get_highs_metrics(filtered_data_without_opponent),
                    )

            def season_graphs():
                if is_percentage:
                    display_data = filtered_data_without_opponent.with_columns(
                        pl.col(selected_metric).mul(100).name.keep()
                    )
                else:  # If not percentage, keep original values
                    display_data = filtered_data_without_opponent
                splits_df = get_away_home_split_df(
                    filtered_data_without_opponent,
                    selected_metric,
                    opponent=selected_opponent,
                )
                # Format values for display
                if is_percentage:
                    splits_df = splits_df.with_columns(
                        pl.col("value").mul(100).round(1)
                    )
                    y_suffix = "%"

                else:
                    splits_df = splits_df.with_columns(pl.col("value").round(1))
                    y_suffix = ""

                # Show home/away bar chart
                location_fig = location_bar_chart(splits_df, selected_metric, y_suffix)
                with st.expander(
                    f"Home/Away {selected_metric} Comparison", expanded=True
                ):
                    st.plotly_chart(location_fig, use_container_width=True)

                # Show season metric chart using the new chart function
                fig = season_metric_chart(
                    display_data,
                    splits_df,
                    metric_name,
                    selected_metric,
                    opponent=selected_opponent,
                    y_suffix=y_suffix,
                )
                with st.expander("Season Progression", expanded=True):
                    st.plotly_chart(fig, use_container_width=True)

            two_column_layout(
                left_content=season_stats_card,
                right_content=season_graphs,
                left_width=1,
                right_width=3,
            )

        def show_career_graphs():
            # Prepare career data by season
            career_data = filtered_data_without_season
            if career_data.is_empty():
                st.info("No career data available for the selected filters.")
                return

            # Summary stats card
            def summary_stats_card():
                with st.expander("Career Totals", expanded=True):
                    # Display career totals card
                    totals_card(
                        *get_totals_metrics(career_data),
                    )

                # Career highs against selected team
                with st.expander("Career Highs", expanded=True):
                    # Get career highs
                    highs_card(
                        *get_highs_metrics(career_data),
                    )

            def career_graphs():
                # Aggregate data by season
                season_data = (
                    career_data.group_by("season")
                    .agg(
                        pl.mean(selected_metric).alias(selected_metric),
                        pl.count("game_id").alias("games_played"),
                    )
                    .sort("season")
                )

                # Apply formatting for percentage metrics
                if is_percentage:
                    season_data = season_data.with_columns(
                        pl.col(selected_metric).mul(100).round(1)
                    )

                # Display career progression chart
                metric_display = (
                    f"Average {metric_name.title()}{'%' if is_percentage else ''}"
                )
                fig = career_metric_chart(
                    season_data, selected_metric, metric_display, with_annotations=True
                )
                with st.expander("Career Progression", expanded=True):
                    st.plotly_chart(fig, use_container_width=True)

                # Shooting statistics chart
                with st.expander("Shooting Statistics by Season", expanded=True):
                    # Create season-by-season shooting stats
                    shooting_data = get_shooting_stats(career_data)

                    # Selector for shooting stats to display
                    shooting_stats_options = [
                        "Field Goals",
                        "2-Point Shots",
                        "3-Point Shots",
                        "Free Throws",
                    ]
                    shooting_stats_selected = st.multiselect(
                        "Select Shooting Stats to Display",
                        options=shooting_stats_options,
                        default=shooting_stats_options,
                    )

                    if shooting_stats_selected:
                        fig_shooting = player_shot_chart(
                            shooting_data, shooting_stats_selected
                        )
                        if fig_shooting:
                            st.plotly_chart(fig_shooting, use_container_width=True)
                    else:
                        st.info(
                            "Please select at least one shooting statistic type to display"
                        )

            if career_data.is_empty():
                st.info("No career data available for the selected filters.")
                return
            else:
                two_column_layout(
                    left_content=summary_stats_card,
                    right_content=career_graphs,
                    left_width=1,
                    right_width=3,
                )

        def show_game_log():
            if filtered_data.is_empty():
                st.info("No data available for the selected filters.")
                return
            # Get player game log
            game_log = prepare_player_season_stats(
                filtered_data,
                opponent=selected_opponent
                if selected_opponent != "All Teams"
                else None,
            )

            # Show game log table
            if not game_log.is_empty():
                stats_table(game_log, column_config=PLAYER_GAME_LOG_COLUMN_CONFIG)
            else:
                st.info("No game log data available for the selected filters.")

        # Create tabbed interface
        tabbed_interface(
            {
                "Global stats": show_global_stats,
                "Season graphs": show_season_graphs,
                "Career graphs": show_career_graphs,
                "Game Log": show_game_log,
            }
        )

    else:
        st.warning(f"No data found for player '{player_name}'.")
else:
    st.info("Enter a player name or select a player from another page.")
