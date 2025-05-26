"""
Column Mapping Utilities
Functions for mapping between database column names and display column names.
"""

import polars as pl
from typing import Dict
from utils.players import get_player_photo_url
from utils.teams import get_team_logo_url

# Team column mappings from database to display names
TEAMS_COLUMN_MAPPING = {
    "pts": "points",
    "mp": "minutes_played",
    "fg": "made_field_goal",
    "fga": "attempted_field_goal",
    "fg_pct": "field_goal_percent",
    "three_p": "made_three_point",
    "three_pa": "attempted_three_point",
    "three_p_pct": "three_point_percent",
    "two_p": "made_two_point",
    "two_pa": "attempted_two_point",
    "two_p_pct": "two_point_percent",
    "ft": "made_free_throw",
    "fta": "attempted_free_throw",
    "ft_pct": "free_throw_percent",
    "orb": "offensive_rebounds",
    "drb": "defensive_rebounds",
    "trb": "rebounds",
    "ast": "assists",
    "stl": "steals",
    "blk": "blocks",
    "tov": "turnovers",
    "pf": "personal_fouls",
}

# Player column mappings from database to display names
PLAYERS_COLUMN_MAPPING = {
    "mp": "minutes_played",
    "fg": "made_field_goal",
    "fga": "attempted_field_goal",
    "fg_pct": "field_goal_percent",
    "three_p": "made_three_point",
    "three_pa": "attempted_three_point",
    "three_p_pct": "three_point_percent",
    "two_p": "made_two_point",
    "two_pa": "attempted_two_point",
    "two_p_pct": "two_point_percent",
    "ft": "made_free_throw",
    "fta": "attempted_free_throw",
    "ft_pct": "free_throw_percent",
    "orb": "offensive_rebounds",
    "drb": "defensive_rebounds",
    "trb": "rebounds",
    "ast": "assists",
    "stl": "steals",
    "blk": "blocks",
    "tov": "turnovers",
    "pf": "personal_fouls",
    "pts": "points",
    "plus_minus": "plus_minus",
    # Keep "starter" as is
}


def rename_df_columns(df: pl.DataFrame, column_mapping: Dict[str, str]) -> pl.DataFrame:
    """
    Rename columns in a DataFrame based on a mapping dictionary.

    Args:
        df: DataFrame to rename columns in
        column_mapping: Dictionary mapping old column names to new column names

    Returns:
        DataFrame with renamed columns
    """
    df_renamed = df.clone()

    for old_name, new_name in column_mapping.items():
        if old_name in df.columns:
            df_renamed = df_renamed.rename({old_name: new_name})

    return df_renamed


def add_player_photo_url(df: pl.DataFrame) -> pl.DataFrame:
    """
    Add a column with the player's photo URL to the DataFrame.

    Args:
        df (pl.DataFrame): The DataFrame containing player data.

    Returns:
        pl.DataFrame: The DataFrame with an additional column for player photo URLs.
    """
    return df.with_columns(
        pl.col("player_id")
        .map_elements(lambda x: get_player_photo_url(x), return_dtype=pl.String)
        .alias("photo_url"),
    )


def add_team_logo_url(df: pl.DataFrame) -> pl.DataFrame:
    """
    Add a column with the team's logo URL to the DataFrame.

    Args:
        df (pl.DataFrame): The DataFrame containing team data.

    Returns:
        pl.DataFrame: The DataFrame with an additional column for team logo URLs.
    """
    return df.with_columns(
        pl.col("team")
        .map_elements(lambda x: get_team_logo_url(x), return_dtype=pl.String)
        .alias("team_logo_url"),
    )
