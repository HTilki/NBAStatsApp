"""
Game Data Processing Module
Functions for processing game data and filtering.
"""

import polars as pl
from typing import List, Any, Union, Tuple, Dict

from data.column_mapping import (
    PLAYERS_COLUMN_MAPPING,
    rename_df_columns,
)
from utils.formatting import format_stats_for_display, format_sp_into_mp


def prepare_players_boxscore(
    players_data: pl.DataFrame, stats_columns: List[str], include_sorting: bool = True
) -> pl.DataFrame:
    """
    Prepare players boxscore data for display.

    Args:
        players_data: Raw players boxscore data
        stats_columns: List of columns to include
        include_sorting: Whether to add sorting columns

    Returns:
        Processed DataFrame ready for display
    """
    # Apply column mapping
    players_data_mapped = rename_df_columns(players_data, PLAYERS_COLUMN_MAPPING)

    # Convert seconds played to minutes played format if needed
    if (
        "seconds_played" in players_data_mapped.columns
        and "minutes_played" not in players_data_mapped.columns
    ):
        players_data_mapped = format_sp_into_mp(players_data_mapped, format="time")

    # Include team and player_id in available columns if present
    base_cols = stats_columns.copy()
    if "team" in players_data_mapped.columns and "team" not in base_cols:
        base_cols.append("team")
    if "player_id" in players_data_mapped.columns and "player_id" not in base_cols:
        base_cols.append("player_id")

    # Select columns that exist in the data
    available_cols = [col for col in base_cols if col in players_data_mapped.columns]
    players_display_data = players_data_mapped.select(available_cols)

    # Add sorting values if requested
    if include_sorting:
        return players_display_data.with_columns(
            [
                # Check if minutes_played is one of the DNP values
                pl.when(
                    pl.col("minutes_played")
                    .str.to_lowercase()
                    .is_in(
                        [
                            "did not play",
                            "not with team",
                            "did not dress",
                            "player suspended",
                        ]
                    )
                )
                .then(0)  # If DNP, set played_value to 0
                .otherwise(1)  # If played, set played_value to 1
                .alias("played_value"),
            ]
        ).pipe(format_stats_for_display)
    else:
        return players_display_data


def filter_data_by_game_filters(
    df: pl.DataFrame, filters: Dict[str, Any]
) -> pl.DataFrame:
    """
    Apply common game filters to a DataFrame.

    Args:
        df: DataFrame to filter
        filters: dictionary of filter conditions

    Returns:
        Filtered DataFrame
    """
    filtered_df = df

    # Apply season filter
    if "season" in filters and "season" in filtered_df.columns:
        if filters["season"] != "All Seasons":
            filtered_df = filtered_df.filter(pl.col("season") == filters["season"])

    # Apply game type filter
    if "game_type" in filters and "game_type" in filtered_df.columns:
        if filters["game_type"] != "all":
            if filters["game_type"] == "regular season":
                filtered_df = filtered_df.filter(
                    (pl.col("game_type").str.to_lowercase() == "regular season")
                    | (
                        (
                            pl.col("game_type").str.to_lowercase()
                            == "in-season tournament"
                        )
                        & (
                            pl.col("game_remarks").str.to_lowercase()
                            != "championship game"
                        )
                    )
                )
            filtered_df = filtered_df.filter(
                pl.col("game_type").str.to_lowercase() == filters["game_type"]
            )

    # Apply team filter
    if "team" in filters:
        if "team" in filtered_df.columns:
            filtered_df = filtered_df.filter(pl.col("team") == filters["team"])
        elif "home_team" in filtered_df.columns and "away_team" in filtered_df.columns:
            filtered_df = filtered_df.filter(
                (pl.col("home_team") == filters["team"])
                | (pl.col("away_team") == filters["team"])
            )

    # Apply opponent filter
    if "opponent" in filters and "opponent" in filtered_df.columns:
        if filters["opponent"] != "All Teams":
            filtered_df = filtered_df.filter(pl.col("opponent") == filters["opponent"])

    # Apply date range filters
    if "date_from" in filters and "date" in filtered_df.columns:
        filtered_df = filtered_df.filter(pl.col("date") >= filters["date_from"])

    if "date_to" in filters and "date" in filtered_df.columns:
        filtered_df = filtered_df.filter(pl.col("date") <= filters["date_to"])

    return filtered_df


def prepare_game_result_data(
    games_df: pl.DataFrame, group_by_date: bool = True, sort_desc: bool = True
) -> Union[pl.DataFrame, Tuple[pl.DataFrame, pl.DataFrame]]:
    """
    Prepare game results data for display, optionally grouped by date.

    Args:
        games_df: DataFrame with game results
        group_by_date: Whether to group games by date
        sort_desc: Whether to sort by date descending

    Returns:
        If group_by_date is True: Tuple of (games_df, dates_df)
        If group_by_date is False: games_df
    """
    if games_df.is_empty():
        if group_by_date:
            return games_df, pl.DataFrame()
        return games_df

    # Add date string column for display
    games_with_date = games_df.with_columns(
        pl.col("date").cast(pl.String).alias("date_str")
    )

    # Sort by date
    sorted_games = games_with_date.sort(
        "date", descending=sort_desc, maintain_order=True
    )

    if group_by_date:
        # Get unique dates
        dates = (
            sorted_games.select("date", "date_str")
            .unique()
            .sort(by="date", descending=sort_desc)
        )
        return sorted_games, dates

    return sorted_games
