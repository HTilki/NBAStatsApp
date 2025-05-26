"""
Data Processing Module
Core data processing functions for the NBA Stats App.
This module contains utility functions for data analysis and aggregation.
"""

import polars as pl
from typing import Literal, Union


def prepare_season_stats(
    season_data: pl.DataFrame, stat_type: str = "team", min_games: int = 0
) -> pl.DataFrame:
    """
    Prepare season stats data for display.

    Args:
        season_data: Raw season stats data
        stat_type: "team" or "player"
        min_games: Minimum games played (for player stats)

    Returns:
        Processed season stats DataFrame
    """
    if season_data.is_empty():
        return season_data

    # Apply minimum games filter for players
    if stat_type == "player" and min_games > 0:
        season_data = season_data.filter(pl.col("games_played") >= min_games)

    # Format percentage columns
    percentage_cols = ["fg_pct", "three_p_pct", "ft_pct", "two_p_pct"]
    if stat_type == "team":
        percentage_cols.append("win_pct")

    # Apply formatting to percentages
    for col in percentage_cols:
        if col in season_data.columns:
            season_data = season_data.with_columns(
                pl.col(col).mul(100).round(1).alias(col)
            )

    return season_data


def get_totals_metrics(
    data: pl.DataFrame, type: Literal["career", "season"] = "career"
) -> tuple:
    """
    Prepare career/season metrics data for display.

    Args:
        data: Raw career/season metrics data

    Returns:
        Processed career/season metrics DataFrame
    """
    if type == "career":
        group_by_col = "season"
    elif type == "season":
        group_by_col = "player_name"
    if data.is_empty():
        return data
    else:
        metrics = (
            data.group_by(group_by_col)
            .agg(
                pl.count("game_id").alias("games_played"),
                pl.sum("points").alias("total_points"),
                pl.sum("assists").alias("total_assists"),
                pl.sum("rebounds").alias("rebounds_sum"),
                pl.sum("steals").alias("total_steals"),
                pl.sum("blocks").alias("total_blocks"),
                pl.sum("made_field_goal").alias("total_fg"),
                pl.sum("attempted_field_goal").alias("total_fga"),
                pl.sum("made_two_point").alias("total_2p"),
                pl.sum("attempted_two_point").alias("total_2pa"),
                pl.sum("made_three_point").alias("total_3p"),
                pl.sum("attempted_three_point").alias("total_3pa"),
                pl.sum("made_free_throw").alias("total_ft"),
                pl.sum("attempted_free_throw").alias("total_fta"),
            )
            .sort("season")
        )
        total_games = metrics.select(pl.sum("games_played")).item()
        total_points = metrics.select(pl.sum("total_points")).item()
        rebounds = metrics.select(pl.sum("rebounds_sum")).item()
        total_assists = metrics.select(pl.sum("total_assists")).item()
        total_fg = metrics.select(pl.sum("total_fg")).item()
        total_fga = metrics.select(pl.sum("total_fga")).item()
        total_2p = metrics.select(pl.sum("total_2p")).item()
        total_2pa = metrics.select(pl.sum("total_2pa")).item()
        total_3p = metrics.select(pl.sum("total_3p")).item()
        total_3pa = metrics.select(pl.sum("total_3pa")).item()
        total_ft = metrics.select(pl.sum("total_ft")).item()
        total_fta = metrics.select(pl.sum("total_fta")).item()
        wins = data.filter(pl.col("outcome") == 1).height
        losses = data.filter(pl.col("outcome") == 0).height

        return (
            total_games,
            total_points,
            rebounds,
            total_assists,
            total_fg,
            total_fga,
            total_2p,
            total_2pa,
            total_3p,
            total_3pa,
            total_ft,
            total_fta,
            wins,
            losses,
        )


def get_highs_metrics(data: pl.DataFrame) -> tuple:
    """
    Prepare career highs data for display.
    Args:
        data: Raw career highs data
    Returns:
        Processed career highs DataFrame
    """
    points_high = data.select(pl.max("points")).item()
    rebounds_high = data.select(pl.max("rebounds")).item()
    assists_high = data.select(pl.max("assists")).item()
    fg_high = data.select(pl.max("made_field_goal")).item()
    fg3_high = data.select(pl.max("made_three_point")).item()
    # Add date of career highs
    high_points_game = data.filter(pl.col("points") == points_high).select(
        ["date", "opponent"]
    )[0]
    high_rebounds_game = data.filter(pl.col("rebounds") == rebounds_high).select(
        ["date", "opponent"]
    )[0]
    high_assists_game = data.filter(pl.col("assists") == assists_high).select(
        ["date", "opponent"]
    )[0]
    high_fg_game = data.filter(pl.col("made_field_goal") == fg_high).select(
        ["date", "opponent"]
    )[0]
    high_fg3_game = data.filter(pl.col("made_three_point") == fg3_high).select(
        ["date", "opponent"]
    )[0]
    return (
        points_high,
        rebounds_high,
        assists_high,
        fg_high,
        fg3_high,
        high_points_game,
        high_rebounds_game,
        high_assists_game,
        high_fg_game,
        high_fg3_game,
    )


def get_shooting_stats(data: pl.DataFrame) -> pl.DataFrame:
    """
    Prepare shooting data for display.
    Args:
        data: Raw shooting data

    Returns
        Processed shooting data DataFrame
    """
    # Create season-by-season shooting stats
    return (
        data.group_by("season")
        .agg(
            pl.mean("field_goal_percent").alias("fg_pct"),
            pl.mean("made_field_goal").alias("fgm"),
            pl.mean("attempted_field_goal").alias("fga"),
            pl.mean("two_point_percent").alias("two_p_pct"),
            pl.mean("made_two_point").alias("two_pm"),
            pl.mean("attempted_two_point").alias("two_pa"),
            pl.mean("three_point_percent").alias("three_p_pct"),
            pl.mean("made_three_point").alias("three_pm"),
            pl.mean("attempted_three_point").alias("three_pa"),
            pl.mean("free_throw_percent").alias("ft_pct"),
            pl.mean("made_free_throw").alias("ftm"),
            pl.mean("attempted_free_throw").alias("fta"),
            pl.count("game_id").alias("games_played"),
        )
        .with_columns(
            pl.col("fg_pct").mul(100).round(2).alias("fg_pct"),
            pl.col("two_p_pct").mul(100).round(2).alias("two_p_pct"),
            pl.col("three_p_pct").mul(100).round(2).alias("three_p_pct"),
            pl.col("ft_pct").mul(100).round(2).alias("ft_pct"),
        )
        .sort("season")
    )


def get_away_home_split_df(
    data: pl.DataFrame, metric: str, opponent: str
) -> pl.DataFrame:
    """
    Prepare away/home split data for display.
    Args:
        data: Raw data
        metric: Metric to split by (e.g., "points", "rebounds")
        opponent: Opponent to filter by
    Returns:
        Processed away/home split data DataFrame
    """

    splits_data = []

    # Overall average
    overall_avg = data[metric].mean()
    splits_data.append({"Location": "Overall", "value": overall_avg})
    # Home games
    home_avg = data.filter(pl.col("location") == "home")[metric].mean()
    splits_data.append({"Location": "Home", "value": home_avg})
    # Away games
    away_avg = data.filter(pl.col("location") == "away")[metric].mean()
    splits_data.append({"Location": "Away", "value": away_avg})

    # Vs specific team if selected
    if opponent and opponent != "All Teams":
        vs_team_avg = data.filter(pl.col("opponent") == opponent)[metric].mean()
        splits_data.append({"Location": f"vs {opponent}", "value": vs_team_avg})

    return pl.DataFrame(splits_data)


def get_team_overall_stats(data: pl.DataFrame) -> pl.DataFrame:
    """
    Prepare team overall stats data for display.
    Args:
        data: Team data
    Returns:
        Processed team overall stats data DataFrame
    """
    # Calculate overall stats for selected filter
    return (
        data.with_columns(
            pl.when(pl.col("outcome") == 1)
            .then(pl.lit(1))
            .otherwise(pl.lit(0))
            .alias("wins"),
            pl.when(pl.col("outcome") == 0)
            .then(pl.lit(1))
            .otherwise(pl.lit(0))
            .alias("losses"),
        )
        .group_by("team")
        .agg(
            pl.len().alias("games_played"),
            pl.mean("points").round(1).alias("ppg"),
            pl.mean("rebounds").round(1).alias("rpg"),
            pl.mean("assists").round(1).alias("apg"),
            pl.mean("steals").round(1).alias("spg"),
            pl.mean("blocks").round(1).alias("bpg"),
            pl.mean("field_goal_percent").alias("fg_pct"),
            pl.mean("three_point_percent").alias("three_p_pct"),
            pl.mean("attempted_three_point").alias("three_pa"),
            pl.mean("free_throw_percent").alias("ft_pct"),
            pl.sum("wins").name.keep(),
            pl.sum("losses").name.keep(),
        )
        .with_columns(
            pl.col("fg_pct").round(3).alias("fg_pct"),
            pl.col("three_p_pct").round(3).alias("three_p_pct"),
            pl.col("ft_pct").round(3).alias("ft_pct"),
        )
    )


def get_team_season_stats(data: pl.DataFrame) -> pl.DataFrame:
    """
    Prepare team season stats data for display.
    Args:
        data: Team data
    Returns:
        Processed team season stats data DataFrame
    """
    return (
        data.with_columns(
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
            pl.mean("rebounds").round(1).alias("rpg"),
            pl.mean("assists").round(1).alias("apg"),
            pl.mean("steals").round(1).alias("spg"),
            pl.mean("blocks").round(1).alias("bpg"),
            pl.mean("made_field_goal").alias("fgm"),
            pl.mean("attempted_field_goal").alias("fga"),
            pl.mean("field_goal_percent").alias("fg_pct"),
            pl.mean("made_three_point").alias("three_pm"),
            pl.mean("attempted_three_point").alias("three_pa"),
            pl.mean("three_point_percent").alias("three_p_pct"),
            pl.mean("free_throw_percent").alias("ft_pct"),
            pl.sum("wins").name.keep(),
            pl.sum("losses").name.keep(),
        )
        .sort("season", descending=True)
        .with_columns(
            pl.col("fg_pct").mul(100).round(1).alias("fg_pct"),
            pl.col("three_p_pct").mul(100).round(1).alias("three_p_pct"),
            pl.col("ft_pct").mul(100).round(1).alias("ft_pct"),
        )
    )


def get_win_percentage_data(
    data: pl.DataFrame, opponent: str
) -> list[dict[str, Union[str, float]]]:
    """
    Prepare win percentage data for win percentage chart.
    Args:
        data: DataFrame with game results
        opponent: Opponent to filter by
    Returns:
        List of dictionaries with win percentage data

    """
    # Create win percentage data
    win_pct_data = []

    # Overall win percentage
    overall_wins = data.filter(pl.col("outcome") == 1).height
    overall_losses = data.filter(pl.col("outcome") == 0).height
    if overall_wins + overall_losses > 0:
        overall_win_pct = overall_wins / (overall_wins + overall_losses)
        win_pct_data.append({"Team": "Overall", "value": overall_win_pct})

    # Home win percentage
    home_games = data.filter(pl.col("location") == "home")
    home_wins = home_games.filter(pl.col("outcome") == 1).height
    home_losses = home_games.filter(pl.col("outcome") == 0).height
    if home_wins + home_losses > 0:
        home_win_pct = home_wins / (home_wins + home_losses)
        win_pct_data.append({"Team": "Home", "value": home_win_pct})

    # Away win percentage
    away_games = data.filter(pl.col("location") == "away")
    away_wins = away_games.filter(pl.col("outcome") == 1).height
    away_losses = away_games.filter(pl.col("outcome") == 0).height
    if away_wins + away_losses > 0:
        away_win_pct = away_wins / (away_wins + away_losses)
        win_pct_data.append({"Team": "Away", "value": away_win_pct})

    # Add opponent if selected
    if opponent != "All Teams":
        vs_opp = data.filter(pl.col("opponent") == opponent)
        vs_opp_wins = vs_opp.filter(pl.col("outcome") == 1).height
        vs_opp_losses = vs_opp.filter(pl.col("outcome") == 0).height
        if vs_opp_wins + vs_opp_losses > 0:
            vs_opp_win_pct = vs_opp_wins / (vs_opp_wins + vs_opp_losses)
            win_pct_data.append({"Team": f"vs {opponent}", "value": vs_opp_win_pct})

    return win_pct_data


def get_against_opponents_stats(data: pl.DataFrame) -> pl.DataFrame:
    """
    Prepare stats against opponent data for display.
    Args:
        data: DataFrame with game results
    Returns:
        Processed stats against opponent DataFrame
    """
    # Calculate stats against each opponent
    return (
        data.with_columns(
            pl.when(pl.col("outcome") == 1)
            .then(pl.lit(1))
            .otherwise(pl.lit(0))
            .alias("wins"),
            pl.when(pl.col("outcome") == 0)
            .then(pl.lit(1))
            .otherwise(pl.lit(0))
            .alias("losses"),
        )
        .group_by("opponent")
        .agg(
            pl.len().alias("games_played"),
            pl.mean("points").round(1).alias("ppg"),
            pl.mean("rebounds").round(1).alias("rpg"),
            pl.mean("assists").round(1).alias("apg"),
            pl.mean("steals").round(1).alias("spg"),
            pl.mean("blocks").round(1).alias("bpg"),
            pl.mean("attempted_field_goal").alias("fga"),
            pl.mean("made_field_goal").alias("fgm"),
            pl.mean("field_goal_percent").mul(100).round(1).alias("fg_pct"),
            pl.mean("attempted_three_point").alias("three_pa"),
            pl.mean("made_three_point").alias("three_pm"),
            pl.mean("three_point_percent").mul(100).round(1).alias("three_p_pct"),
            pl.mean("attempted_free_throw").alias("fta"),
            pl.mean("made_free_throw").alias("ftm"),
            pl.mean("free_throw_percent").mul(100).round(1).alias("ft_pct"),
            pl.sum("wins").name.keep(),
            pl.sum("losses").name.keep(),
        )
        .sort("opponent")
        .with_columns(
            (pl.col("wins") / (pl.col("wins") + pl.col("losses")))
            .round(3)
            .alias("win_pct")
        )
        .select(
            [
                "opponent",
                "games_played",
                "win_pct",
                "ppg",
                "rpg",
                "apg",
                "spg",
                "bpg",
                "fg_pct",
                "three_p_pct",
                "fga",
                "fgm",
                "three_pa",
                "three_pm",
                "fta",
                "ftm",
                "ft_pct",
                "wins",
                "losses",
            ]
        )
    )


def get_team_season_trend(data: pl.DataFrame) -> pl.DataFrame:
    return (
        data.with_columns(
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
            pl.mean("three_point_percent").mul(100).round(1).alias("three_p_pct"),
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
