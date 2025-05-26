"""
Column Configuration Module
Defines column configurations for Streamlit dataframes.
"""

import streamlit as st

# Player statistics columns to display
PLAYERS_STATS_COLUMNS = [
    "player_name",
    "starter",
    "minutes_played",
    "points",
    "made_field_goal",
    "attempted_field_goal",
    "field_goal_percent",
    "made_three_point",
    "attempted_three_point",
    "three_point_percent",
    "made_free_throw",
    "attempted_free_throw",
    "free_throw_percent",
    "offensive_rebounds",
    "defensive_rebounds",
    "rebounds",
    "assists",
    "steals",
    "blocks",
    "turnovers",
    "personal_fouls",
    "plus_minus",
]

# Team statistics columns to display
TEAMS_STATS_COLUMNS = [
    "team",
    "points",
    "made_field_goal",
    "attempted_field_goal",
    "field_goal_percent",
    "made_three_point",
    "attempted_three_point",
    "three_point_percent",
    "made_free_throw",
    "attempted_free_throw",
    "free_throw_percent",
    "offensive_rebounds",
    "defensive_rebounds",
    "rebounds",
    "assists",
    "steals",
    "blocks",
    "turnovers",
    "personal_fouls",
]

# Column configuration for player statistics
PLAYERS_COLUMN_CONFIG = {
    "photo_url": st.column_config.ImageColumn("", help="Player photo"),
    "player_name": st.column_config.TextColumn("Player", help="Player's name"),
    "starter": st.column_config.CheckboxColumn(
        "Starter", help="Whether player started the game"
    ),
    "minutes_played": st.column_config.TextColumn("MIN", help="Minutes played"),
    "points": st.column_config.NumberColumn("PTS", help="Total points scored"),
    "made_field_goal": st.column_config.NumberColumn("FGM", help="Field goals made"),
    "attempted_field_goal": st.column_config.NumberColumn(
        "FGA", help="Field goals attempted"
    ),
    "field_goal_percent": st.column_config.TextColumn(
        "FG%", help="Field goal percentage (FGM/FGA)"
    ),
    "made_three_point": st.column_config.NumberColumn(
        "3PM", help="Three-pointers made"
    ),
    "attempted_three_point": st.column_config.NumberColumn(
        "3PA", help="Three-pointers attempted"
    ),
    "three_point_percent": st.column_config.TextColumn(
        "3P%", help="Three-point percentage (3PM/3PA)"
    ),
    "made_free_throw": st.column_config.NumberColumn("FTM", help="Free throws made"),
    "attempted_free_throw": st.column_config.NumberColumn(
        "FTA", help="Free throws attempted"
    ),
    "free_throw_percent": st.column_config.TextColumn(
        "FT%", help="Free throw percentage (FTM/FTA)"
    ),
    "offensive_rebounds": st.column_config.NumberColumn(
        "ORB", help="Offensive rebounds"
    ),
    "defensive_rebounds": st.column_config.NumberColumn(
        "DRB", help="Defensive rebounds"
    ),
    "rebounds": st.column_config.NumberColumn("TRB", help="Total rebounds"),
    "assists": st.column_config.NumberColumn("AST", help="Assists"),
    "steals": st.column_config.NumberColumn("STL", help="Steals"),
    "blocks": st.column_config.NumberColumn("BLK", help="Blocks"),
    "turnovers": st.column_config.NumberColumn("TOV", help="Turnovers"),
    "personal_fouls": st.column_config.NumberColumn("PF", help="Personal fouls"),
    "plus_minus": st.column_config.NumberColumn(
        "+/-", help="Plus-minus score while on court"
    ),
}

# Column configuration for team statistics
TEAM_COLUMN_CONFIG = {
    "team_logo_url": st.column_config.ImageColumn("", help="Team logo"),
    "team": st.column_config.TextColumn("Team", help="Team name"),
    "points": st.column_config.NumberColumn("PTS", help="Total points scored"),
    "made_field_goal": st.column_config.NumberColumn("FGM", help="Field goals made"),
    "attempted_field_goal": st.column_config.NumberColumn(
        "FGA", help="Field goals attempted"
    ),
    "field_goal_percent": st.column_config.TextColumn(
        "FG%", help="Field goal percentage (FGM/FGA)"
    ),
    "made_three_point": st.column_config.NumberColumn(
        "3PM", help="Three-pointers made"
    ),
    "attempted_three_point": st.column_config.NumberColumn(
        "3PA", help="Three-pointers attempted"
    ),
    "three_point_percent": st.column_config.TextColumn(
        "3P%", help="Three-point percentage (3PM/3PA)"
    ),
    "made_free_throw": st.column_config.NumberColumn("FTM", help="Free throws made"),
    "attempted_free_throw": st.column_config.NumberColumn(
        "FTA", help="Free throws attempted"
    ),
    "free_throw_percent": st.column_config.TextColumn(
        "FT%", help="Free throw percentage (FTM/FTA)"
    ),
    "offensive_rebounds": st.column_config.NumberColumn(
        "ORB", help="Offensive rebounds"
    ),
    "defensive_rebounds": st.column_config.NumberColumn(
        "DRB", help="Defensive rebounds"
    ),
    "rebounds": st.column_config.NumberColumn("TRB", help="Total rebounds"),
    "assists": st.column_config.NumberColumn("AST", help="Assists"),
    "steals": st.column_config.NumberColumn("STL", help="Steals"),
    "blocks": st.column_config.NumberColumn("BLK", help="Blocks"),
    "turnovers": st.column_config.NumberColumn("TOV", help="Turnovers"),
    "personal_fouls": st.column_config.NumberColumn("PF", help="Personal fouls"),
}

TEAM_STAT_AGG_COLUMN_CONFIG = {
    "season": st.column_config.TextColumn("Season", help="NBA season"),
    "team": st.column_config.TextColumn("Team", help="Team name"),
    "games_played": st.column_config.NumberColumn(
        "GP", help="Games played", width="small"
    ),
    "wins": st.column_config.NumberColumn(
        "Wins", help="Wins this season", width="small"
    ),
    "losses": st.column_config.NumberColumn(
        "Losses", help="Losses this season", width="small"
    ),
    "win_pct": st.column_config.NumberColumn(
        "Win%", help="Win percentage", format="%.3f", width="small"
    ),
    "ppg": st.column_config.NumberColumn(
        "PPG", format="%.1f", help="Points per game", width="small"
    ),
    "rpg": st.column_config.NumberColumn(
        "RPG", format="%.1f", help="Rebounds per game", width="small"
    ),
    "apg": st.column_config.NumberColumn(
        "APG", format="%.1f", help="Assists per game", width="small"
    ),
    "spg": st.column_config.NumberColumn(
        "SPG", format="%.1f", help="Steals per game", width="small"
    ),
    "bpg": st.column_config.NumberColumn(
        "BPG", format="%.1f", help="Blocks per game", width="small"
    ),
    "fga": st.column_config.NumberColumn(
        "FGA", format="%.1f", help="Field goals attempted per game", width="small"
    ),
    "fgm": st.column_config.NumberColumn(
        "FGM", format="%.1f", help="Field goals made per game", width="small"
    ),
    "fg_pct": st.column_config.NumberColumn(
        "FG%", format="%.1f", help="Field goal percentage", width="small"
    ),
    "three_pa": st.column_config.NumberColumn(
        "3PA", format="%.1f", help="Three-pointers attempted per game", width="small"
    ),
    "three_pm": st.column_config.NumberColumn(
        "3PM", format="%.1f", help="Three-pointers made per game", width="small"
    ),
    "three_p_pct": st.column_config.NumberColumn(
        "3P%", format="%.1f", help="Three-point percentage", width="small"
    ),
    "fta": st.column_config.NumberColumn(
        "FTA", format="%.1f", help="Free throws attempted per game", width="small"
    ),
    "ftm": st.column_config.NumberColumn(
        "FTM", format="%.1f", help="Free throws made per game", width="small"
    ),
    "ft_pct": st.column_config.NumberColumn(
        "FT%", format="%.1f", help="Free throw percentage", width="small"
    ),
}


# Player aggregated statistics column config
PLAYER_STAT_AGG_COLUMN_CONFIG = {
    "player_name": st.column_config.TextColumn("Player", help="Player's name"),
    "season": st.column_config.TextColumn("Season", help="NBA season"),
    "team": st.column_config.TextColumn("Team", help="Team name", width="small"),
    "games_played": st.column_config.NumberColumn(
        "GP", help="Games played", width="small"
    ),
    "ppg": st.column_config.NumberColumn(
        "PPG", format="%.1f", help="Points per game", width="small"
    ),
    "rpg": st.column_config.NumberColumn(
        "RPG", format="%.1f", help="Rebounds per game", width="small"
    ),
    "apg": st.column_config.NumberColumn(
        "APG", format="%.1f", help="Assists per game", width="small"
    ),
    "spg": st.column_config.NumberColumn(
        "SPG", format="%.1f", help="Steals per game", width="small"
    ),
    "bpg": st.column_config.NumberColumn(
        "BPG", format="%.1f", help="Blocks per game", width="small"
    ),
    "fg_per_game": st.column_config.NumberColumn(
        "FGM", format="%.1f", help="Field goals made per game", width="small"
    ),
    "fga_per_game": st.column_config.NumberColumn(
        "FGA", format="%.1f", help="Field goals attempted per game", width="small"
    ),
    "fg_pct": st.column_config.NumberColumn(
        "FG%", format="%.1f", help="Field goal percentage", width="small"
    ),
    "three_p_per_game": st.column_config.NumberColumn(
        "3PM", format="%.1f", help="Three-pointers made per game", width="small"
    ),
    "three_pa_per_game": st.column_config.NumberColumn(
        "3PA", format="%.1f", help="Three-pointers attempted per game", width="small"
    ),
    "three_p_pct": st.column_config.NumberColumn(
        "3P%", format="%.1f", help="Three-point percentage", width="small"
    ),
    "two_p_per_game": st.column_config.NumberColumn(
        "2PM", format="%.1f", help="Two-pointers made per game", width="small"
    ),
    "two_pa_per_game": st.column_config.NumberColumn(
        "2PA", format="%.1f", help="Two-pointers attempted per game", width="small"
    ),
    "two_p_pct": st.column_config.NumberColumn(
        "2P%", format="%.1f", help="Two-point percentage", width="small"
    ),
    "ft_per_game": st.column_config.NumberColumn(
        "FTM", format="%.1f", help="Free throws made per game", width="small"
    ),
    "fta_per_game": st.column_config.NumberColumn(
        "FTA", format="%.1f", help="Free throws attempted per game", width="small"
    ),
    "ft_pct": st.column_config.NumberColumn(
        "FT%", format="%.1f", help="Free throw percentage", width="small"
    ),
    # "minutes_per_game": st.column_config.NumberColumn("MPG", format="%.1f", help="Minutes played per game"),
}


TEAM_SEASON_STATS_COLUMN_CONFIG = {
    "rank": st.column_config.NumberColumn("#", pinned=True, width="small"),
    "team": st.column_config.TextColumn("Team"),
    "wins": st.column_config.NumberColumn("W", width="small"),
    "losses": st.column_config.NumberColumn("L", width="small"),
    "games_played": st.column_config.NumberColumn(
        "GP", width="small", help="Games Played"
    ),
    "ppg": st.column_config.NumberColumn(
        "PPG", format="%.1f", help="Points Per Game", width="small"
    ),
    "points_allowed": st.column_config.NumberColumn(
        "PA", format="%.1f", help="Points Allowed", width="small"
    ),
    "rpg": st.column_config.NumberColumn(
        "RPG", format="%.1f", width="small", help="Rebounds Per Game"
    ),
    "orpg": st.column_config.NumberColumn(
        "ORPG", format="%.1f", width="small", help="Offensive Rebounds Per Game"
    ),
    "drpg": st.column_config.NumberColumn(
        "DRPG", format="%.1f", width="small", help="Defensive Rebounds Per Game"
    ),
    "apg": st.column_config.NumberColumn(
        "APG", format="%.1f", width="small", help="Assists Per Game"
    ),
    "spg": st.column_config.NumberColumn(
        "SPG", format="%.1f", width="small", help="Steals Per Game"
    ),
    "bpg": st.column_config.NumberColumn(
        "BPG", format="%.1f", width="small", help="Blocks Per Game"
    ),
    "tpg": st.column_config.NumberColumn(
        "TOPG", format="%.1f", width="small", help="Turnovers Per Game"
    ),
    "fg": st.column_config.NumberColumn(
        "FGM", format="%.1f", width="small", help="Field Goals Made Per Game"
    ),
    "fga": st.column_config.NumberColumn(
        "FGA", format="%.1f", width="small", help="Field Goals Attempted Per Game"
    ),
    "fg_pct": st.column_config.TextColumn(
        "FG%", width="small", help="Field Goal Percentage"
    ),
    "three_p": st.column_config.NumberColumn(
        "3PM", format="%.1f", width="small", help="3-Points Made Per Game"
    ),
    "three_pa": st.column_config.NumberColumn(
        "3PA", format="%.1f", width="small", help="3-Points Attempted Per Game"
    ),
    "three_p_pct": st.column_config.TextColumn(
        "3P%", width="small", help="3-Point Percentage"
    ),
    "two_ppg": st.column_config.NumberColumn(
        "2PM", format="%.1f", width="small", help="2-Points Made Per Game"
    ),
    "two_papg": st.column_config.NumberColumn(
        "2PA", format="%.1f", width="small", help="2-Points Attempted Per Game"
    ),
    "two_p_pct": st.column_config.TextColumn(
        "2P%", width="small", help="2-Point Percentage"
    ),
    "ft": st.column_config.NumberColumn(
        "FTM", format="%.1f", width="small", help="Free Throws Made Per Game"
    ),
    "fta": st.column_config.NumberColumn(
        "FTA", format="%.1f", width="small", help="Free Throws Attempted Per Game"
    ),
    "ft_pct": st.column_config.TextColumn(
        "FT%", width="small", help="Free Throw Percentage"
    ),
}

PLAYER_SEASON_STATS_COLUMN_CONFIG = {
    "rank": st.column_config.NumberColumn(
        "#", pinned=True, width="small", help="Player ranking"
    ),
    "player": st.column_config.TextColumn("Player", help="Player's full name"),
    "games_played": st.column_config.NumberColumn(
        "GP", width="small", help="Games played during the season"
    ),
    "ppg": st.column_config.NumberColumn(
        "PPG", format="%.1f", width="small", help="Points per game"
    ),
    "rpg": st.column_config.NumberColumn(
        "RPG", format="%.1f", width="small", help="Total rebounds per game"
    ),
    "orpg": st.column_config.NumberColumn(
        "ORPG",
        format="%.1f",
        width="small",
        help="Offensive rebounds per game",
    ),
    "drpg": st.column_config.NumberColumn(
        "DRPG",
        format="%.1f",
        width="small",
        help="Defensive rebounds per game",
    ),
    "apg": st.column_config.NumberColumn(
        "APG", format="%.1f", width="small", help="Assists per game"
    ),
    "spg": st.column_config.NumberColumn(
        "SPG", format="%.1f", width="small", help="Steals per game"
    ),
    "bpg": st.column_config.NumberColumn(
        "BPG", format="%.1f", width="small", help="Blocks per game"
    ),
    "tpg": st.column_config.NumberColumn(
        "TOPG",
        format="%.1f",
        width="small",
        help="Turnovers per game",
    ),
    "fg": st.column_config.NumberColumn(
        "FGM",
        format="%.1f",
        width="small",
        help="Field goals made per game",
    ),
    "fga": st.column_config.NumberColumn(
        "FGA",
        format="%.1f",
        width="small",
        help="Field goals attempted per game",
    ),
    "fg_pct": st.column_config.NumberColumn(
        "FG%",
        format="%.1f",
        width="small",
        help="Field goal shooting percentage (FGM/FGA)",
    ),
    "two_ppg": st.column_config.NumberColumn(
        "2PM",
        format="%.1f",
        width="small",
        help="2-point field goals made per game",
    ),
    "two_papg": st.column_config.NumberColumn(
        "2PA",
        format="%.1f",
        width="small",
        help="2-point field goals attempted per game",
    ),
    "two_p_pct": st.column_config.TextColumn(
        "2P%", width="small", help="2-point shooting percentage (2PM/2PA)"
    ),
    "three_p": st.column_config.NumberColumn(
        "3PM",
        format="%.1f",
        width="small",
        help="3-point field goals made per game",
    ),
    "three_pa": st.column_config.NumberColumn(
        "3PA",
        format="%.1f",
        width="small",
        help="3-point field goals attempted per game",
    ),
    "three_p_pct": st.column_config.TextColumn(
        "3P%", width="small", help="3-point shooting percentage (3PM/3PA)"
    ),
    "ft": st.column_config.NumberColumn(
        "FTM",
        format="%.1f",
        width="small",
        help="Free throws made per game",
    ),
    "fta": st.column_config.NumberColumn(
        "FTA",
        format="%.1f",
        width="small",
        help="Free throws attempted per game",
    ),
    "ft_pct": st.column_config.TextColumn(
        "FT%", width="small", help="Free throw shooting percentage (FTM/FTA)"
    ),
    "avg_minutes": st.column_config.NumberColumn(
        "MPG", format="%.1f", width="small", help="Minutes played per game"
    ),
}

PLAYER_GAME_LOG_COLUMN_CONFIG = {
    "home_team": st.column_config.TextColumn("Home Team", help="Home team name"),
    "away_team": st.column_config.TextColumn("Away Team", help="Away team name"),
    "home_team_pts": st.column_config.NumberColumn("Home Pts", help="Home team points"),
    "away_team_pts": st.column_config.NumberColumn("Away Pts", help="Away team points"),
    "date": st.column_config.DateColumn("Date", help="Game date"),
    "result": st.column_config.TextColumn("Result", help="Game result (WIN/LOSS)"),
    "minutes_played": st.column_config.TextColumn(
        "MIN", help="Minutes played", width="small"
    ),
    "points": st.column_config.NumberColumn(
        "PTS", help="Total points scored", width="small"
    ),
    "made_field_goal": st.column_config.NumberColumn(
        "FGM", help="Field goals made", width="small"
    ),
    "attempted_field_goal": st.column_config.NumberColumn(
        "FGA", help="Field goals attempted", width="small"
    ),
    "field_goal_percent": st.column_config.TextColumn(
        "FG%", help="Field goal percentage", width="small"
    ),
    "made_three_point": st.column_config.NumberColumn(
        "3PM", help="Three-pointers made", width="small"
    ),
    "attempted_three_point": st.column_config.NumberColumn(
        "3PA", help="Three-pointers attempted", width="small"
    ),
    "three_point_percent": st.column_config.TextColumn(
        "3P%", help="Three-point percentage", width="small"
    ),
    "made_free_throw": st.column_config.NumberColumn(
        "FTM", help="Free throws made", width="small"
    ),
    "attempted_free_throw": st.column_config.NumberColumn(
        "FTA", help="Free throws attempted", width="small"
    ),
    "free_throw_percent": st.column_config.TextColumn(
        "FT%", help="Free throw percentage", width="small"
    ),
    "rebounds": st.column_config.NumberColumn(
        "REB", help="Total rebounds", width="small"
    ),
    "assists": st.column_config.NumberColumn("AST", help="Assists", width="small"),
    "steals": st.column_config.NumberColumn("STL", help="Steals", width="small"),
    "blocks": st.column_config.NumberColumn("BLK", help="Blocks", width="small"),
    "turnovers": st.column_config.NumberColumn("TOV", help="Turnovers", width="small"),
    "plus_minus": st.column_config.NumberColumn(
        "+/-", help="Plus-minus score while on court", width="small"
    ),
}

TEAM_GAME_LOG_COLUMN_CONFIG = {
    "date": st.column_config.DateColumn("Date", help="Game date"),
    "game_type": st.column_config.TextColumn("Game Type", help="Type of game"),
    "opponent": st.column_config.TextColumn("Opponent", help="Opponent team"),
    "location": st.column_config.TextColumn("Location", help="Game location"),
    "result": st.column_config.CheckboxColumn("Result", help="Game result"),
    "points": st.column_config.NumberColumn(
        "PTS", help="Total points scored", width="small"
    ),
    "assists": st.column_config.NumberColumn(
        "AST", help="Total assists", width="small"
    ),
    "offensive_rebounds": st.column_config.NumberColumn(
        "OREB", help="Offensive rebounds", width="small"
    ),
    "defensive_rebounds": st.column_config.NumberColumn(
        "DREB", help="Defensive rebounds", width="small"
    ),
    "rebounds": st.column_config.NumberColumn(
        "REB", help="Total rebounds", width="small"
    ),
    "steals": st.column_config.NumberColumn("STL", help="Steals", width="small"),
    "blocks": st.column_config.NumberColumn("BLK", help="Blocks", width="small"),
    "turnovers": st.column_config.NumberColumn("TOV", help="Turnovers", width="small"),
    "attempted_field_goal": st.column_config.NumberColumn(
        "FGA", help="Field goals attempted", width="small"
    ),
    "made_field_goal": st.column_config.NumberColumn(
        "FGM", help="Field goals made", width="small"
    ),
    "field_goal_percent": st.column_config.TextColumn(
        "FG%", help="Field goal percentage", width="small"
    ),
    "attempted_three_point": st.column_config.NumberColumn(
        "3PA", help="Three-pointers attempted", width="small"
    ),
    "made_three_point": st.column_config.NumberColumn(
        "3PM", help="Three-pointers made", width="small"
    ),
    "three_point_percent": st.column_config.TextColumn(
        "3P%", help="Three-point percentage", width="small"
    ),
    "attempted_free_throw": st.column_config.NumberColumn(
        "FTA", help="Free throws attempted", width="small"
    ),
    "made_free_throw": st.column_config.NumberColumn(
        "FTM", help="Free throws made", width="small"
    ),
    "free_throw_percent": st.column_config.TextColumn(
        "FT%", help="Free throw percentage", width="small"
    ),
}

[
    "opponent",
    "games_played",
    "win_pct",
    "ppg",
    "apg",
    "rpg",
    "spg",
    "bpg",
    "fga",
    "fgm",
    "fg_pct",
    "three_pa",
    "three_pm",
    "three_p_pct",
    "fta",
    "ftm",
    "ft_pct",
    "wins",
    "losses",
]
OPPONENT_STAT_AGG_COLUMN_CONFIG = {
    "opponent": st.column_config.TextColumn("Opponent", help="Opponent team"),
    "games_played": st.column_config.NumberColumn(
        "GP", help="Games played against opponent"
    ),
    "win_pct": st.column_config.NumberColumn(
        "Win%", format="%.3f", help="Win percentage against opponent"
    ),
    "ppg": st.column_config.NumberColumn(
        "PPG", format="%.1f", help="Points per game against opponent", width="small"
    ),
    "apg": st.column_config.NumberColumn(
        "APG", format="%.1f", help="Assists per game against opponent", width="small"
    ),
    "rpg": st.column_config.NumberColumn(
        "RPG", format="%.1f", help="Rebounds per game against opponent", width="small"
    ),
    "spg": st.column_config.NumberColumn(
        "SPG", format="%.1f", help="Steals per game against opponent", width="small"
    ),
    "bpg": st.column_config.NumberColumn(
        "BPG", format="%.1f", help="Blocks per game against opponent", width="small"
    ),
    "fga": st.column_config.NumberColumn(
        "FGA",
        format="%.1f",
        help="Field goals attempted per game against opponent",
        width="small",
    ),
    "fgm": st.column_config.NumberColumn(
        "FGM",
        format="%.1f",
        help="Field goals made per game against opponent",
        width="small",
    ),
    "fg_pct": st.column_config.NumberColumn(
        "FG%",
        format="%.1f",
        help="Field goal percentage per game against opponent",
        width="small",
    ),
    "three_pa": st.column_config.NumberColumn(
        "3PA",
        format="%.1f",
        help="Three-pointers attempted per game against opponent",
        width="small",
    ),
    "three_pm": st.column_config.NumberColumn(
        "3PM",
        format="%.1f",
        help="Three-pointers made per games against opponent",
        width="small",
    ),
    "three_p_pct": st.column_config.NumberColumn(
        "3P%",
        format="%.1f",
        help="Three-point percentage per game against opponent",
        width="small",
    ),
    "fta": st.column_config.NumberColumn(
        "FTA",
        format="%.1f",
        help="Free throws attempted per game against opponent",
        width="small",
    ),
    "ftm": st.column_config.NumberColumn(
        "FTM",
        format="%.1f",
        help="Free throws made per game against opponent",
        width="small",
    ),
    "ft_pct": st.column_config.NumberColumn(
        "FT%",
        format="%.1f",
        help="Free throw percentage per game against opponent",
        width="small",
    ),
    "wins": st.column_config.NumberColumn(
        "Wins", help="Wins against opponent", width="small"
    ),
    "losses": st.column_config.NumberColumn(
        "Losses", help="Losses against opponent", width="small"
    ),
}
