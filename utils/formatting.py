"""
Formatting Utilities
Consolidated formatting functions for data display and UI elements.
Includes data formatters and team utility functions.
"""

import datetime
import polars as pl
from typing import Literal


def format_percentage_columns(df: pl.DataFrame) -> pl.DataFrame:
    """
    Format percentage columns to show with % sign and proper decimal places.

    Args:
        df: DataFrame with percentage columns

    Returns:
        DataFrame with formatted percentage columns
    """
    if df.is_empty():
        return df

    percentage_cols = [
        col for col in df.columns if col.endswith("_pct") or col.endswith("_percent")
    ]

    for col in percentage_cols:
        if col in df.columns:
            df = df.with_columns(
                pl.when(pl.col(col).is_null())
                .then(pl.lit(""))
                .otherwise((pl.col(col) * 100).round(1).cast(pl.Utf8) + "%")
                .alias(col)
            )

    return df


def format_numeric_columns(df: pl.DataFrame) -> pl.DataFrame:
    """
    Format numeric columns for better display.

    Args:
        df: DataFrame with numeric columns

    Returns:
        DataFrame with formatted numeric columns
    """
    if df.is_empty():
        return df

    # Round decimal columns to 1 place
    decimal_cols = [
        col for col in df.columns if col.endswith("_per_game") or col.endswith("pg")
    ]

    for col in decimal_cols:
        if col in df.columns:
            df = df.with_columns(pl.col(col).round(1))

    return df


def format_stats_for_display(df: pl.DataFrame) -> pl.DataFrame:
    """
    Format player/team statistics for display in tables.

    Args:
        df: DataFrame with statistics

    Returns:
        Formatted DataFrame ready for display
    """
    if df.is_empty():
        return df

    return df.pipe(format_percentage_columns).pipe(format_numeric_columns)


def format_seconds_to_minutes(
    df: pl.DataFrame,
    seconds_col: str = "seconds_played",
    format_type: Literal["time", "str", "float"] = "time",
) -> pl.DataFrame:
    """
    Convert seconds to minutes with different format options.

    Args:
        df: DataFrame with seconds column
        seconds_col: Name of the seconds column
        format_type: Output format - "time" (MM:SS), "str" (MM:SS), or "float" (decimal minutes)

    Returns:
        DataFrame with formatted minutes column
    """
    if df.is_empty() or seconds_col not in df.columns:
        return df

    if format_type == "float":
        # Convert to decimal minutes
        df = df.with_columns(
            (pl.col(seconds_col) / 60).round(1).alias("minutes_played")
        )
    else:
        # Convert to MM:SS format
        df = (
            df.with_columns(
                [
                    (pl.col(seconds_col) // 60).alias("minutes"),
                    (pl.col(seconds_col) % 60).alias("seconds"),
                ]
            )
            .with_columns(
                pl.when(pl.col("seconds") < 10)
                .then(
                    pl.col("minutes").cast(pl.Utf8)
                    + ":0"
                    + pl.col("seconds").cast(pl.Utf8)
                )
                .otherwise(
                    pl.col("minutes").cast(pl.Utf8)
                    + ":"
                    + pl.col("seconds").cast(pl.Utf8)
                )
                .alias("minutes_played")
            )
            .drop(["minutes", "seconds"])
        )

    return df


def format_game_result(home_score: int, away_score: int, is_home: bool = True) -> str:
    """
    Format game result as W or L.

    Args:
        home_score: Home team score
        away_score: Away team score
        is_home: Whether the perspective is from the home team

    Returns:
        "W" for win, "L" for loss
    """
    if is_home:
        return "W" if home_score > away_score else "L"
    else:
        return "W" if away_score > home_score else "L"


def format_datetime_for_display(
    dt: datetime.datetime, format_str: str = "%Y-%m-%d"
) -> str:
    """
    Format datetime for UI display.

    Args:
        dt: DateTime object to format
        format_str: Format string for datetime display

    Returns:
        Formatted datetime string
    """
    return dt.strftime(format_str)


# Legacy alias for backward compatibility
def format_sp_into_mp(
    df: pl.DataFrame, format: Literal["time", "str", "float"] = "time"
) -> pl.DataFrame:
    """
    Legacy function - use format_seconds_to_minutes instead.

    Args:
        df: DataFrame with seconds_played column
        format: Output format type

    Returns:
        DataFrame with minutes_played column
    """
    return format_seconds_to_minutes(df, format_type=format)
