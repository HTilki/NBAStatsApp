"""
Team Data Processing Module
Functions specifically for processing and preparing team data.
"""

import polars as pl
from typing import List

from data.column_mapping import (
    TEAMS_COLUMN_MAPPING,
    rename_df_columns,
    add_team_logo_url,
)
from utils.formatting import format_stats_for_display
from data.cast_types import cast_boxscore_columns


def prepare_teams_boxscore(
    teams_data: pl.DataFrame, stats_columns: List[str]
) -> pl.DataFrame:
    """
    Prepare teams boxscore data for display.

    Args:
        teams_data: Raw teams boxscore data
        stats_columns: List of columns to include

    Returns:
        Processed DataFrame ready for display
    """
    # Apply column mapping
    teams_data_renamed = rename_df_columns(teams_data, TEAMS_COLUMN_MAPPING)

    # Select columns that exist in the data
    available_columns = [
        col for col in stats_columns if col in teams_data_renamed.columns
    ]

    # Format for display and add team logos
    return (
        teams_data_renamed.select(available_columns)
        .pipe(format_stats_for_display)
        .pipe(add_team_logo_url)
        .select(["team_logo_url"] + available_columns)
    )


def prepare_team_data(
    team_data_raw: pl.DataFrame,
) -> pl.DataFrame:
    """
    Prepare team data for display.

    Args:
        team_data_raw: Raw team data

    Returns:
        Processed team data
    """

    # Apply column mapping
    team_data = rename_df_columns(team_data_raw, TEAMS_COLUMN_MAPPING)

    # Cast columns to appropriate data types
    team_data = cast_boxscore_columns(team_data, is_player_boxscore=False)

    return team_data


def prepare_team_game_log(
    team_data: pl.DataFrame,
) -> pl.DataFrame:
    """
    Prepare team season game-by-game statistics.

    Args:
        team_data: Processed team data

    Returns:
        Game log DataFrame
    """
    # Sort by game date
    game_log = team_data.sort("date", descending=True).select(
        [
            "date",
            "game_type",
            "opponent",
            "location",
            "outcome",
            "points",
            "assists",
            "offensive_rebounds",
            "defensive_rebounds",
            "rebounds",
            "steals",
            "blocks",
            "turnovers",
            "attempted_field_goal",
            "made_field_goal",
            "field_goal_percent",
            "attempted_three_point",
            "made_three_point",
            "three_point_percent",
            "attempted_free_throw",
            "made_free_throw",
            "free_throw_percent",
        ]
    )

    # Format percentage columns
    if not game_log.is_empty():
        game_log = game_log.with_columns(
            [
                pl.col("game_type").str.to_titlecase().alias("game_type"),
                pl.col("location").str.to_titlecase().alias("location"),
                pl.when(pl.col("outcome") == 1)
                .then(True)
                .otherwise(False)
                .alias("outcome"),
                pl.col("field_goal_percent")
                .mul(100)
                .round(1)
                .alias("field_goal_percent"),
                pl.col("three_point_percent")
                .mul(100)
                .round(1)
                .alias("three_point_percent"),
                pl.col("free_throw_percent")
                .mul(100)
                .round(1)
                .alias("free_throw_percent"),
            ]
        ).rename({"outcome": "result"})

    return game_log
