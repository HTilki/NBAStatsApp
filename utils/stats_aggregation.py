"""
Statistics Aggregation and Calculation Module
Core statistical functions for aggregating and calculating NBA statistics.
"""

import polars as pl
from typing import Dict
from data.cast_types import clean_percentage_values


def aggregate_player_stats(
    df: pl.DataFrame, group_by: str = "player_name"
) -> pl.DataFrame:
    """
    Aggregate player statistics with proper calculations.

    Args:
        df: DataFrame with individual game player statistics
        group_by: Column to group by (default: player_name)

    Returns:
        DataFrame with aggregated player statistics
    """
    if df.is_empty():
        return pl.DataFrame()

    # Ensure required columns exist
    required_cols = [
        "points",
        "rebounds",
        "assists",
        "steals",
        "blocks",
        "made_field_goal",
        "attempted_field_goal",
        "made_two_point",
        "attempted_two_point",
        "made_three_point",
        "attempted_three_point",
        "made_free_throw",
        "attempted_free_throw",
        "seconds_played",
    ]

    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        for col in missing_cols:
            df = df.with_columns(pl.lit(None).alias(col))

    # Calculate aggregated statistics
    agg_df = df.group_by(group_by).agg(
        [
            pl.len().alias("games_played"),
            pl.mean("points").alias("ppg"),
            pl.mean("rebounds").alias("rpg"),
            pl.mean("assists").alias("apg"),
            pl.mean("steals").alias("spg"),
            pl.mean("blocks").alias("bpg"),
            (pl.sum("made_field_goal") / pl.sum("attempted_field_goal")).alias(
                "fg_pct"
            ),
            (pl.sum("made_two_point") / pl.sum("attempted_two_point")).alias(
                "two_p_pct"
            ),
            (pl.sum("made_three_point") / pl.sum("attempted_three_point")).alias(
                "three_p_pct"
            ),
            (pl.sum("made_free_throw") / pl.sum("attempted_free_throw")).alias(
                "ft_pct"
            ),
            (pl.mean("seconds_played") / 60).alias("minutes_per_game"),
            pl.mean("made_field_goal").alias("fg_per_game"),
            pl.mean("attempted_field_goal").alias("fga_per_game"),
            pl.mean("made_two_point").alias("two_p_per_game"),
            pl.mean("attempted_two_point").alias("two_pa_per_game"),
            pl.mean("made_three_point").alias("three_p_per_game"),
            pl.mean("attempted_three_point").alias("three_pa_per_game"),
            pl.mean("made_free_throw").alias("ft_per_game"),
            pl.mean("attempted_free_throw").alias("fta_per_game"),
        ]
    )

    return clean_percentage_values(agg_df)


def calculate_win_loss_record(df: pl.DataFrame) -> Dict[str, int]:
    """
    Calculate win-loss record from game outcome data.

    Args:
        df: DataFrame with game data containing 'outcome' column

    Returns:
        Dictionary with wins and losses counts
    """
    if df.is_empty() or "outcome" not in df.columns:
        return {"wins": 0, "losses": 0}

    wins = df.filter(pl.col("outcome") == 1).height
    losses = df.filter(pl.col("outcome") == 0).height

    return {"wins": wins, "losses": losses}


def calculate_shooting_percentages(df: pl.DataFrame) -> pl.DataFrame:
    """
    Calculate shooting percentages from made/attempted columns.

    Args:
        df: DataFrame with made/attempted shooting columns

    Returns:
        DataFrame with calculated shooting percentages
    """
    if df.is_empty():
        return df

    # Field goal percentage
    if "made_field_goal" in df.columns and "attempted_field_goal" in df.columns:
        df = df.with_columns(
            (pl.col("made_field_goal") / pl.col("attempted_field_goal")).alias(
                "field_goal_percent"
            )
        )

    # Three point percentage
    if "made_three_point" in df.columns and "attempted_three_point" in df.columns:
        df = df.with_columns(
            (pl.col("made_three_point") / pl.col("attempted_three_point")).alias(
                "three_point_percent"
            )
        )

    # Free throw percentage
    if "made_free_throw" in df.columns and "attempted_free_throw" in df.columns:
        df = df.with_columns(
            (pl.col("made_free_throw") / pl.col("attempted_free_throw")).alias(
                "free_throw_percent"
            )
        )

    return df


def filter_by_season(df: pl.DataFrame, season: str) -> pl.DataFrame:
    """
    Filter DataFrame by season.

    Args:
        df: DataFrame with season column
        season: Season to filter by

    Returns:
        Filtered DataFrame
    """
    if df.is_empty() or "season" not in df.columns:
        return df

    return df.filter(pl.col("season") == season)


def join_with_schedule(df: pl.DataFrame, schedule: pl.DataFrame) -> pl.DataFrame:
    """
    Join statistics data with schedule information.

    Args:
        df: DataFrame with game statistics (must have game_id column)
        schedule: DataFrame with schedule data

    Returns:
        Joined DataFrame with schedule information
    """
    if df.is_empty() or "game_id" not in df.columns:
        return df

    schedule_cols = [
        "id",
        "date",
        "season",
        "home_team",
        "away_team",
        "home_pts",
        "away_pts",
        "game_type",
    ]

    available_schedule_cols = [col for col in schedule_cols if col in schedule.columns]

    return df.join(
        schedule.select(available_schedule_cols),
        left_on="game_id",
        right_on="id",
    )


# Legacy function aliases for backward compatibility
player_stat_agg = aggregate_player_stats
join_schedule = join_with_schedule
filter_games_by_season = filter_by_season
