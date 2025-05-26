"""
Data Type Casting Module
Functions for casting DataFrame columns to appropriate data types.
"""

import polars as pl


def cast_boxscore_columns(
    data: pl.DataFrame, is_player_boxscore: bool = True
) -> pl.DataFrame:
    """
    Cast boxscore DataFrame columns to appropriate data types.

    Args:
        data: DataFrame to cast
        is_player_boxscore: Whether the DataFrame is a player boxscore (True) or team boxscore (False)

    Returns:
        DataFrame with properly typed columns
    """
    # Set string columns
    string_cols = ["game_id", "team", "opponent", "location"]
    if is_player_boxscore:
        string_cols.append("player_name")

    # Cast string columns
    for col in string_cols:
        if col in data.columns:
            data = data.with_columns(pl.col(col).cast(pl.String))

    # Cast boolean column for player boxscore
    if is_player_boxscore and "starter" in data.columns:
        data = data.with_columns(
            pl.when(pl.col("starter") == 1).then(True).otherwise(False).alias("starter")
        )

    # Use the appropriate casting function based on boxscore type
    if is_player_boxscore:
        return cast_players_boxscore_columns(data)
    else:
        return cast_teams_boxscore_columns(data)


def cast_players_boxscore_columns(data: pl.DataFrame) -> pl.DataFrame:
    """
    Cast player boxscore columns to appropriate data types.

    Converts statistical columns to proper numeric types (Int32 for counts, Float64 for percentages).

    Args:
        data: Player boxscore data with string columns

    Returns:
        DataFrame with columns cast to appropriate numeric types
    """

    return data.with_columns(
        pl.col("made_field_goal").cast(pl.Int32, strict=False),
        pl.col("attempted_field_goal").cast(pl.Int32, strict=False),
        pl.col("field_goal_percent").cast(pl.Float64, strict=False),
        pl.col("made_three_point").cast(pl.Int32, strict=False),
        pl.col("attempted_three_point").cast(pl.Int32, strict=False),
        pl.col("three_point_percent").cast(pl.Float64, strict=False),
        pl.col("made_two_point").cast(pl.Int32, strict=False),
        pl.col("attempted_two_point").cast(pl.Int32, strict=False),
        pl.col("two_point_percent").cast(pl.Float64, strict=False),
        pl.col("made_free_throw").cast(pl.Int32, strict=False),
        pl.col("attempted_free_throw").cast(pl.Int32, strict=False),
        pl.col("free_throw_percent").cast(pl.Float64, strict=False),
        pl.col("offensive_rebounds").cast(pl.Int32, strict=False),
        pl.col("defensive_rebounds").cast(pl.Int32, strict=False),
        pl.col("rebounds").cast(pl.Int32, strict=False),
        pl.col("assists").cast(pl.Int32, strict=False),
        pl.col("steals").cast(pl.Int32, strict=False),
        pl.col("blocks").cast(pl.Int32, strict=False),
        pl.col("turnovers").cast(pl.Int32, strict=False),
        pl.col("personal_fouls").cast(pl.Int32, strict=False),
        pl.col("points").cast(pl.Int32, strict=False),
        pl.col("plus_minus").cast(pl.Int32, strict=False),
    )


def cast_teams_boxscore_columns(data: pl.DataFrame) -> pl.DataFrame:
    """
    Cast team boxscore columns to appropriate data types.

    Converts statistical columns to proper numeric types (Int32 for counts, Float64 for percentages).

    Args:
        data: Team boxscore data with string columns

    Returns:
        DataFrame with columns cast to appropriate numeric types
    """
    # First handle empty strings in all columns
    for col in data.columns:
        if col not in ["team", "opponent", "location", "game_id"]:
            data = data.with_columns(
                pl.when(pl.col(col).cast(pl.String) == "")
                .then(None)
                .otherwise(pl.col(col))
                .alias(col)
            )

    return data.with_columns(
        pl.col("minutes_played").cast(pl.Int32, strict=False),
        pl.col("made_field_goal").cast(pl.Int32, strict=False),
        pl.col("attempted_field_goal").cast(pl.Int32, strict=False),
        pl.col("field_goal_percent").cast(pl.Float64, strict=False),
        pl.col("made_three_point").cast(pl.Int32, strict=False),
        pl.col("attempted_three_point").cast(pl.Int32, strict=False),
        pl.col("three_point_percent").cast(pl.Float64, strict=False),
        pl.col("made_two_point").cast(pl.Int32, strict=False),
        pl.col("attempted_two_point").cast(pl.Int32, strict=False),
        pl.col("two_point_percent").cast(pl.Float64, strict=False),
        pl.col("made_free_throw").cast(pl.Int32, strict=False),
        pl.col("attempted_free_throw").cast(pl.Int32, strict=False),
        pl.col("free_throw_percent").cast(pl.Float64, strict=False),
        pl.col("offensive_rebounds").cast(pl.Int32, strict=False),
        pl.col("defensive_rebounds").cast(pl.Int32, strict=False),
        pl.col("rebounds").cast(pl.Int32, strict=False),
        pl.col("assists").cast(pl.Int32, strict=False),
        pl.col("steals").cast(pl.Int32, strict=False),
        pl.col("blocks").cast(pl.Int32, strict=False),
        pl.col("turnovers").cast(pl.Int32, strict=False),
        pl.col("personal_fouls").cast(pl.Int32, strict=False),
        pl.col("points").cast(pl.Int32, strict=False),
    )


def clean_percentage_values(df: pl.DataFrame) -> pl.DataFrame:
    """
    Clean percentage values ensuring they are in proper format (0-1 range).

    Args:
        df: DataFrame with percentage columns

    Returns:
        DataFrame with cleaned percentage columns
    """
    percentage_cols = [
        col for col in df.columns if col.endswith("_percent") or col.endswith("_pct")
    ]

    for col in percentage_cols:
        if col in df.columns:
            df = df.with_columns(
                pl.when(pl.col(col) > 1.0)
                .then(pl.col(col) / 100.0)
                .otherwise(pl.col(col))
                .alias(col)
            )

    return df
