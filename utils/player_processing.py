"""
Player Data Processing Module
Functions specifically for processing and preparing player data.
"""

import polars as pl
import streamlit as st
from typing import Optional, Tuple, Dict, Any

from utils.stats_aggregation import player_stat_agg, calculate_win_loss_record
from data.column_mapping import (
    PLAYERS_COLUMN_MAPPING,
    rename_df_columns,
    add_player_photo_url,
)
from utils.formatting import (
    format_stats_for_display,
    format_sp_into_mp,
)
from data.cast_types import cast_boxscore_columns
from utils.team_utils import get_team_name_by_abbreviation


def prepare_player_data(
    player_data_raw: pl.DataFrame,
    filters: Optional[Dict[str, Any]] = None,
) -> pl.DataFrame:
    """
    Prepare player data for display.

    Args:
        player_data_raw: Raw player data
        filters: Optional dictionary of filters to apply

    Returns:
        Processed player data"""
    from utils.game_processing import filter_data_by_game_filters

    # Apply column mapping
    player_data = rename_df_columns(player_data_raw, PLAYERS_COLUMN_MAPPING)

    # Cast columns to appropriate data types
    player_data = cast_boxscore_columns(player_data, is_player_boxscore=True)

    # Convert seconds played to minutes played
    player_data = format_sp_into_mp(player_data, format="time")

    # If filters dictionary is provided, use filter_data_by_game_filters
    if filters:
        return filter_data_by_game_filters(player_data, filters)
    else:
        return player_data


def prepare_player_stats_by_game(
    player_data: pl.DataFrame, include_photo: bool = True
) -> pl.DataFrame:
    """
    Prepare player game-by-game statistics for display.

    Args:
        player_data: Raw player statistics data
        include_photo: Whether to add player photo URLs

    Returns:
        Processed DataFrame ready for display
    """
    # Apply column mapping
    player_data_mapped = rename_df_columns(player_data, PLAYERS_COLUMN_MAPPING)

    # Cast columns to appropriate types
    player_data_cast = cast_boxscore_columns(
        player_data_mapped, is_player_boxscore=True
    )

    # Convert seconds played to minutes played format if needed
    if (
        "seconds_played" in player_data_cast.columns
        and "minutes_played" not in player_data_cast.columns
    ):
        player_data_cast = format_sp_into_mp(player_data_cast, format="time")

    # Format for display
    player_data_formatted = format_stats_for_display(player_data_cast)

    # Add photo URL if requested
    if include_photo and "player_id" in player_data_formatted.columns:
        player_data_formatted = add_player_photo_url(player_data_formatted)

    return player_data_formatted


def prepare_player_season_stats(
    player_data: pl.DataFrame,
    opponent: Optional[str] = None,
) -> pl.DataFrame:
    """
    Prepare player season game-by-game statistics.

    Args:
        player_data: Processed player data
        opponent: Optional opponent to filter by

    Returns:
        Game log DataFrame
    """
    # To handle empty DataFrame case
    if player_data.is_empty():
        return player_data
    # Filter by opponent if specified
    if opponent:
        filtered_data = player_data.filter(pl.col("opponent") == opponent)
    else:
        filtered_data = player_data

    # Sort by game date
    game_log = filtered_data.sort("date", descending=True).select(
        [
            "date",
            "home_team",
            "away_team",
            "home_team_pts",
            "away_team_pts",
            "minutes_played",
            "points",
            "assists",
            "rebounds",
            "made_field_goal",
            "attempted_field_goal",
            "field_goal_percent",
            "made_three_point",
            "attempted_three_point",
            "three_point_percent",
            "made_free_throw",
            "attempted_free_throw",
            "free_throw_percent",
            "steals",
            "blocks",
            "turnovers",
            "plus_minus",
        ]
    )
    # Add result column (W/L)
    try:
        game_log = game_log.with_columns(
            [
                pl.when(
                    (
                        pl.col("home_team").str.to_uppercase()
                        == get_team_name_by_abbreviation(
                            teams=st.session_state["teams"],
                            abbreviation=filtered_data[0, "team"],
                        )
                    )
                    & (pl.col("home_team_pts") > pl.col("away_team_pts"))
                )
                .then(pl.lit("WIN"))
                .when(
                    (
                        pl.col("away_team").str.to_uppercase()
                        == get_team_name_by_abbreviation(
                            teams=st.session_state["teams"],
                            abbreviation=filtered_data[0, "team"],
                        )
                    )
                    & (pl.col("away_team_pts") > pl.col("home_team_pts"))
                )
                .then(pl.lit("WIN"))
                .otherwise(pl.lit("LOSS"))
                .alias("result")
            ]
        )
    except AttributeError as e:
        print(f"Error: {e}")
        # Handle case where team abbreviation is not found (means that there are no games)
        return pl.DataFrame()

    # Format percentage columns
    if not game_log.is_empty():
        game_log = game_log.with_columns(
            [
                pl.col("field_goal_percent")
                .mul(100)
                .round(1)
                .alias("field_goal_percent"),
                pl.col("three_point_percent")
                .mul(100)
                .round(1)
                .alias("three_point_percent"),
            ]
        )
    return game_log


def prepare_player_career_stats(
    player_data: pl.DataFrame,
) -> Tuple[pl.DataFrame, pl.DataFrame, Dict[str, int]]:
    """
    Prepare player career statistics.

    Args:
        player_data: Processed player data

    Returns:
        Tuple of (career_stats, career_stats_mean, record)
    """

    # Calculate career stats by season and team
    career_stats = (
        player_stat_agg(player_data, group_by=["player_name", "season", "team"])
        .sort("season", descending=True, maintain_order=True)
        .with_columns(
            pl.col("fg_pct").mul(100).round(2).alias("fg_pct"),
            pl.col("three_p_pct").mul(100).round(2).alias("three_p_pct"),
            pl.col("ft_pct").mul(100).round(2).alias("ft_pct"),
            pl.col("two_p_pct").mul(100).round(2).alias("two_p_pct"),
        )
        .select(
            [
                "season",
                "team",
                "games_played",
                "ppg",
                "rpg",
                "apg",
                "spg",
                "bpg",
                "fg_per_game",
                "fga_per_game",
                "fg_pct",
                "three_p_per_game",
                "three_pa_per_game",
                "three_p_pct",
                "two_p_per_game",
                "two_pa_per_game",
                "two_p_pct",
                "ft_pct",
                "ft_per_game",
                "fta_per_game",
            ]
        )
    )

    # Calculate career stats mean (overall averages)
    career_stats_mean = (
        player_stat_agg(player_data, group_by=["player_name"])
        .with_columns(
            pl.col("fg_pct").mul(100).round(2).alias("fg_pct"),
            pl.col("three_p_pct").mul(100).round(2).alias("three_p_pct"),
            pl.col("ft_pct").mul(100).round(2).alias("ft_pct"),
            pl.col("two_p_pct").mul(100).round(2).alias("two_p_pct"),
        )
        .select(
            [
                "games_played",
                "ppg",
                "rpg",
                "apg",
                "spg",
                "bpg",
                "fg_per_game",
                "fga_per_game",
                "fg_pct",
                "three_p_per_game",
                "three_pa_per_game",
                "three_p_pct",
                "two_p_per_game",
                "two_pa_per_game",
                "two_p_pct",
                "ft_pct",
                "ft_per_game",
                "fta_per_game",
            ]
        )
    )

    # Calculate win-loss record
    record = calculate_win_loss_record(player_data)

    return career_stats, career_stats_mean, record
