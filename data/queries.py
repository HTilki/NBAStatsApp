"""
Database Query Functions for App
Functions for retrieving data from the database for the Streamlit app.
"""

import polars as pl
from psycopg2.extensions import connection
from typing import Dict, List, Any, Optional


def get_teams_boxscore(conn: connection, game_id: str) -> pl.DataFrame:
    """
    Get teams boxscore data for a specific game.

    Args:
        conn: Database connection
        game_id: Game ID

    Returns:
        DataFrame with teams boxscore data
    """
    query = f"""
    SELECT *, 
           (fg - three_p) as two_p,
           (fga - three_pa) as two_pa,
           CASE
               WHEN (fga - three_pa) > 0 THEN (fg - three_p)::float / (fga - three_pa)
               ELSE 0
           END as two_p_pct
    FROM public.teams_boxscore
    WHERE game_id = '{game_id}'
    """
    return pl.read_database(query=query, connection=conn)


def get_players_boxscore(conn: connection, game_id: str) -> pl.DataFrame:
    """
    Get players boxscore data for a specific game.

    Args:
        conn: Database connection
        game_id: Game ID

    Returns:
        DataFrame with players boxscore data
    """
    query = f"""
    SELECT * 
    FROM (
        SELECT * FROM public.players_boxscore
        WHERE game_id = '{game_id}') as pb
    LEFT JOIN (
        SELECT id as player_id, full_name
        FROM nba.players
        ) as p
    ON UPPER(pb.player_name) = UPPER(p.full_name)
    ORDER BY starter DESC, pts DESC
    """
    return pl.read_database(query=query, connection=conn)


def get_player_stats(conn: connection, player_name: str) -> pl.DataFrame:
    """
    Get statistics for a specific player across all games.

    Args:
        conn: Database connection
        player_name: Player name

    Returns:
        DataFrame with player statistics
    """
    query = f"""
    SELECT pb.*, 
           (pb.fg - pb.three_p) as two_p,
           (pb.fga - pb.three_pa) as two_pa,
           CASE
               WHEN (pb.fga - pb.three_pa) > 0 THEN (pb.fg - pb.three_p)::float / (pb.fga - pb.three_pa)
               ELSE 0
           END as two_p_pct,
           s.date, s.season, s.home_team, s.away_team, 
           s.home_team_pts, s.away_team_pts, s.game_type, s.game_remarks
    FROM public.players_boxscore pb
    JOIN public.schedule s ON pb.game_id = s.id
    WHERE UPPER(pb.player_name) = '{player_name.upper()}' 
    AND pb.team IN (SELECT abbreviation FROM public.teams)
    ORDER BY s.date DESC
    """
    return pl.read_database(query=query, connection=conn)


def get_player_season_stats(
    conn: connection,
    season: str = None,
    min_games: Optional[int] = None,
    game_type: str = "all",
) -> pl.DataFrame:
    """
    Get season statistics for all players.

    Args:
        conn: Database connection
        season: Season to filter by (e.g., "2023-2024")
        min_games: Minimum games played to be included
        game_type: Type of game (e.g., "regular season", "playoffs", "all")

    Returns:
        DataFrame with player season statistics
    """
    season_filter = f"AND s.season = '{season}'" if season else ""
    min_games_filter = (
        f"HAVING COUNT(DISTINCT pb.game_id) >= {min_games}" if min_games else ""
    )
    if game_type != "all":
        if game_type == "regular season":
            game_type_filter = " AND UPPER(s.game_type) IN ('REGULAR SEASON', 'IN-SEASON TOURNAMENT') AND UPPER(s.game_remarks) != 'CHAMPIONSHIP GAME'"
        else:
            game_type_filter = f" AND s.game_type = '{game_type}'"
    else:
        game_type_filter = ""
    # mp is in this format: "MM:SS", "Did not play", "Not with team", "Did not dress", "Player suspended"
    # need to convert to float minutes
    # Cast all columns to int and float to avoid type errors
    query = f"""
    WITH players_clean_seconds AS (
        SELECT
            pb.player_name as player,
            pb.game_id,
            CAST (pb.fg AS int) as fg,
            CAST (pb.ft AS int) as ft,
            CAST (pb.fga AS int) as fga,
            CAST (pb.fta AS int) as fta,
            CAST (pb.three_p AS int) as three_p,
            CAST (pb.three_pa AS int) as three_pa,
            (CAST (pb.fg AS int) - CAST (pb.three_p AS int)) as two_p,
            (CAST (pb.fga AS int) - CAST (pb.three_pa AS int)) as two_pa,
            CAST (pb.pts AS int) as pts,
            CAST (pb.trb AS int) as trb,
            CAST (pb.orb AS int) as orb,
            CAST (pb.drb AS int) as drb,
            CAST (pb.ast AS int) as ast,
            CAST (pb.stl AS int) as stl,
            CAST (pb.blk AS int) as blk,
            CAST (pb.tov AS int) as tov,
            CASE
                WHEN UPPER(pb.mp) IN ('DID NOT PLAY', 'NOT WITH TEAM', 'DID NOT DRESS', 'PLAYER SUSPENDED')
                THEN 0
                ELSE CAST(SPLIT_PART(pb.mp, ':', 1) AS float) * 60 + CAST(SPLIT_PART(pb.mp, ':', 2) AS float)
            END AS sp
        FROM
            public.players_boxscore as pb
    ),
    player_games AS (
        SELECT 
            pb.player,
            COUNT(DISTINCT pb.game_id) as games_played,
            AVG(pb.sp)/60 as avg_minutes,
            AVG(pb.pts) as ppg,
            AVG(pb.trb) as rpg,
            AVG(pb.orb) as orpg,
            AVG(pb.drb) as drpg,
            AVG(pb.ast) as apg,
            AVG(pb.stl) as spg,
            AVG(pb.blk) as bpg,
            AVG(pb.tov) as tpg,
            AVG(pb.fg) as fg,
            AVG(pb.fga) as fga,
            SUM(pb.fg)::float / NULLIF(SUM(pb.fga), 0) as fg_pct,
            AVG(pb.three_p) as three_p,
            AVG(pb.three_pa) as three_pa,
            SUM(pb.three_p)::float / NULLIF(SUM(pb.three_pa), 0) as three_p_pct,
            AVG(pb.two_p) as two_ppg,
            AVG(pb.two_pa) as two_papg,
            SUM(pb.two_p)::float / NULLIF(SUM(pb.two_pa), 0) as two_p_pct,
            AVG(pb.ft) as ft,
            AVG(pb.fta) as fta,
            SUM(pb.ft)::float / NULLIF(SUM(pb.fta), 0) as ft_pct
        FROM 
            players_clean_seconds AS pb
        JOIN 
            public.schedule s ON pb.game_id = s.id
        WHERE 
            1=1 {season_filter}
            {game_type_filter}
        GROUP BY 
            pb.player
        {min_games_filter}
    )
    SELECT *
    FROM player_games
    ORDER BY ppg DESC
    """

    df = pl.read_database(query=query, connection=conn)

    # Calculate minutes per game
    if not df.is_empty() and "avg_seconds" in df.columns:
        df = df.with_columns(
            (pl.col("avg_seconds") / 60).alias("minutes_per_game")
        ).drop("avg_seconds")

    return df


# Function to get team stats for all games
def get_team_stats(conn, team_abbreviation):
    """
    Get team statistics across all games.
    """
    query = f"""
    SELECT tb.*, 
            (tb.fg - tb.three_p) as two_p,
            (tb.fga - tb.three_pa) as two_pa,
            CASE
                WHEN (tb.fga - tb.three_pa) > 0 THEN (tb.fg - tb.three_p)::float / (tb.fga - tb.three_pa)
                ELSE 0
            END as two_p_pct,
            s.date, s.season, s.home_team, s.away_team,
            s.home_team_pts, s.away_team_pts, s.game_type, s.game_remarks
    FROM public.teams_boxscore tb
    JOIN public.schedule s ON tb.game_id = s.id
    WHERE tb.team = '{team_abbreviation}'
    ORDER BY s.date DESC
    """
    return pl.read_database(query=query, connection=conn)


def get_team_season_stats(
    conn: connection, season: str = None, game_type: str = "all"
) -> pl.DataFrame:
    """
    Get season statistics for all teams.

    Args:
        conn: Database connection
        season: Season to filter by (e.g., "2023-2024")
        game_type: Type of game (e.g., "regular season", "playoffs", "all")

    Returns:
        DataFrame with team season statistics
    """
    season_filter = f"AND s.season = '{season}'" if season else ""
    if game_type != "all":
        if game_type == "regular season":
            game_type_filter = " AND LOWER(s.game_type) IN ('regular season', 'in-season tournament') AND (LOWER(s.game_remarks) != 'championship game' OR s.game_remarks IS NULL)"
        else:
            game_type_filter = f" AND s.game_type = '{game_type}'"
    else:
        game_type_filter = ""
    query = f"""
    WITH team_stats AS (
        SELECT 
            tb.team,
            s.season,
            COUNT(DISTINCT tb.game_id) as games_played,
            SUM(CASE WHEN CAST(tb.outcome AS integer) = 1 THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN CAST(tb.outcome AS integer) = 0 THEN 1 ELSE 0 END) as losses,
            AVG(CAST(tb.fg AS float)) as fg,
            AVG(CAST(tb.fga AS float)) as fga,
            AVG(CAST(tb.fg AS float)/NULLIF(CAST(tb.fga AS float), 0)) as fg_pct,
            AVG(CAST(tb.three_p AS float)) as three_p,
            AVG(CAST(tb.three_pa AS float)) as three_pa,
            AVG(CAST(tb.three_p AS float)/NULLIF(CAST(tb.three_pa AS float), 0)) as three_p_pct,
            AVG(CAST(tb.ft AS float)) as ft,
            AVG(CAST(tb.fta AS float)) as fta,
            AVG(CAST(tb.ft AS float)/NULLIF(CAST(tb.fta AS float), 0)) as ft_pct,
            AVG(CAST((tb.fg - tb.three_p) AS float)) as two_ppg,
            AVG(CAST((tb.fga - tb.three_pa) AS float)) as two_papg,
            AVG(CAST((tb.fg - tb.three_p) AS float)/NULLIF(CAST((tb.fga - tb.three_pa) AS float), 0)) as two_p_pct,
            AVG(CAST(tb.pts AS float)) as ppg,
            AVG(CAST(tb2.pts AS float)) as points_allowed,
            AVG(CAST(tb.trb AS float)) as rpg,
            AVG(CAST(tb.orb AS float)) as orpg,
            AVG(CAST(tb.drb AS float)) as drpg,
            AVG(CAST(tb.tov AS float)) as tpg,
            AVG(CAST(tb.ast AS float)) as apg,
            AVG(CAST(tb.stl AS float)) as spg,
            AVG(CAST(tb.blk AS float)) as bpg
        FROM public.teams_boxscore tb
        JOIN (SELECT game_id, team, opponent, pts FROM public.teams_boxscore) AS tb2 
            ON tb.game_id = tb2.game_id AND (tb.opponent = tb2.team AND tb.team != tb2.team)
        JOIN public.schedule s ON tb.game_id = s.id
        WHERE tb.team = tb2.opponent {season_filter} {game_type_filter}
        GROUP BY tb.team, s.season
    )
    SELECT *
    FROM team_stats
    WHERE team IN (SELECT abbreviation FROM public.teams)
    ORDER BY wins DESC
    """

    return pl.read_database(query=query, connection=conn)


def get_game_schedule(conn: connection, filters: Dict[str, Any] = None) -> pl.DataFrame:
    """
    Get game schedule with optional filters.

    Args:
        conn: Database connection
        filters: Dictionary of filters to apply

    Returns:
        DataFrame with schedule data
    """
    where_clauses = []

    # Build WHERE clause from filters
    if filters:
        if "season" in filters and filters["season"]:
            where_clauses.append(f"season = '{filters['season']}'")
        if (
            "game_type" in filters
            and filters["game_type"]
            and filters["game_type"] != "all"
        ):
            if filters["game_type"] == "regular season":
                where_clauses.append(
                    "UPPER(game_type) IN ('REGULAR SEASON', 'IN-SEASON TOURNAMENT') AND UPPER(game_remarks) != 'CHAMPIONSHIP GAME'"
                )
            else:
                where_clauses.append(
                    f"UPPER(game_type) = '{filters['game_type'].upper()}'"
                )
        if "team" in filters and filters["team"]:
            where_clauses.append(
                f"(UPPER(home_team) = '{filters['team']}' OR UPPER(away_team) = '{filters['team'].upper()}')"
            )
        if "date_from" in filters and filters["date_from"]:
            where_clauses.append(f"date >= '{filters['date_from']}'")
        if "date_to" in filters and filters["date_to"]:
            where_clauses.append(f"date <= '{filters['date_to']}'")

    # Construct complete query
    query = "SELECT * FROM public.schedule"
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    query += " AND home_team_pts != 0 ORDER BY start_time DESC"

    return pl.read_database(query=query, connection=conn, infer_schema_length=None)


def get_teams_list(conn: connection) -> List[Dict[str, Any]]:
    """
    Get list of all teams.

    Args:
        conn: Database connection

    Returns:
        List of team dictionaries
    """
    query = "SELECT * FROM public.teams ORDER BY name"
    df = pl.read_database(query=query, connection=conn)

    if df.is_empty():
        return []

    return df.rows(named=True)


def get_seasons_list(conn: connection) -> List[str]:
    """
    Get list of all seasons available in the database.

    Args:
        conn: Database connection

    Returns:
        List of season strings
    """
    query = "SELECT DISTINCT season FROM public.schedule ORDER BY season DESC"
    df = pl.read_database(query=query, connection=conn)

    if df.is_empty():
        return []

    return df["season"].to_list()


def get_season_stats(
    conn: connection, season: str, stat_type: str, game_type: str
) -> pl.DataFrame:
    """
    Get season statistics for teams or players.

    Args:
        conn: Database connection
        season: Season to filter by (e.g., "2023-2024")
        stat_type: Type of statistics to retrieve ("team" or "player")
        game_type: Type of game (e.g., "regular season", "playoffs", "all")

    Returns:
        DataFrame with season statistics
    """
    if stat_type == "team":
        return get_team_season_stats(conn, season=season, game_type=game_type)
    elif stat_type == "player":
        return get_player_season_stats(conn, season=season, game_type=game_type)
    else:
        raise ValueError("Invalid stat type. Must be 'team' or 'player'.")


def get_season_champion(conn: connection, season: str) -> dict[str, str] | None:
    """
    Get season champion for a specific season.

    Args:
        conn: Database connection
        season: Season to filter by (e.g., "2023-2024")

    Returns:
        DataFrame with season champion data
    """
    query = f"""
    SELECT *
    FROM public.schedule s
    WHERE s.season = '{season}'
    ORDER BY s.date DESC
    LIMIT 1
    """
    last_game = pl.read_database(query=query, connection=conn)
    # Get the winner of the last game by comparing scores
    if not last_game.is_empty():
        if last_game.item(0, "home_team_pts") > last_game.item(0, "away_team_pts"):
            winner = {
                "team_name": last_game["home_team"][0],
                "team_abbreviation": last_game["home_team_abb"][0],
            }
        else:
            winner = {
                "team_name": last_game["away_team"][0],
                "team_abbreviation": last_game["away_team_abb"][0],
            }
        return winner
    else:
        return None
