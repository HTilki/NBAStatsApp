"""
Game Details Page
Displays detailed statistics for a selected NBA game.
"""

import streamlit as st
import polars as pl

from utils.connection import get_connection
from data.queries import get_players_boxscore, get_teams_boxscore
from data.column_config import PLAYERS_STATS_COLUMNS, TEAMS_STATS_COLUMNS
from data.column_mapping import add_player_photo_url
from utils.team_utils import (
    get_team_abbreviation as get_abbreviation,
    get_team_name_by_abbreviation,
)
from utils.app_state import AppState
from utils.team_processing import prepare_teams_boxscore
from utils.game_processing import prepare_players_boxscore
from components.headers import team_matchup_header, page_header
from components.tables import player_stats_table, team_stats_table

# Initialize core state
AppState.initialize_core_state()

# Check if a game is selected
if "selected_game" not in st.session_state or not st.session_state["selected_game"]:
    st.error("No game selected. Please select a game from the Games page.")
    if st.button("Go to Games List"):
        st.switch_page("pages/games_list.py")
    st.stop()
else:
    # Get game information
    game_id = st.session_state.get("selected_game").get("id")
    home_team_name = st.session_state.get("selected_game").get("home_team")
    away_team_name = st.session_state.get("selected_game").get("away_team")

# Get team abbreviations
home_team_abbr = get_abbreviation(
    teams=st.session_state["teams"],
    team_name=home_team_name.upper(),
)
away_team_abbr = get_abbreviation(
    teams=st.session_state["teams"],
    team_name=away_team_name.upper(),
)

# Display game title/header
page_header("Game Details")
team_matchup_header(home_team_name, away_team_name)

# Initialize connection and get data
conn = get_connection()

# Get teams boxscore data
teams_data = get_teams_boxscore(conn, game_id)
teams_display_data = prepare_teams_boxscore(teams_data, TEAMS_STATS_COLUMNS)

# Get players boxscore data
players_data_raw = get_players_boxscore(conn, game_id)
players_display_data = prepare_players_boxscore(players_data_raw, PLAYERS_STATS_COLUMNS)

# Close connection
conn.close()

# Display team stats
st.header("Team Stats")
team_stats_table(
    teams_display_data,
    on_select="rerun",
    selection_mode="single-row",
    key="team_boxscore",
)
# Handle team selection
selected_rows = (
    st.session_state.get("team_boxscore", {}).get("selection", {}).get("rows", [])
)
if selected_rows:
    selected_game = teams_display_data.row(selected_rows[0], named=True)
    if selected_game["team"]:
        team_name = get_team_name_by_abbreviation(
            teams=st.session_state["teams"], abbreviation=selected_game["team"]
        )
        # Set the selected team in session state
        AppState.set_selected_team(team_name=team_name)

        if st.button(f"View {team_name}'s Page"):
            st.switch_page("pages/team_stats.py")

# Create tabs for home and away team players
home_team_players = players_display_data.filter(pl.col("team") == home_team_abbr)
away_team_players = players_display_data.filter(pl.col("team") == away_team_abbr)

# Sort players by:
# 1. Starter status (starters first)
# 2. Did they play (players who played first)
home_team_players = (
    home_team_players.sort(by=["starter", "played_value"], descending=[True, True])
    .drop(["played_value"])
    .pipe(add_player_photo_url)
    .select(["photo_url"] + PLAYERS_STATS_COLUMNS)
)

away_team_players = (
    away_team_players.sort(by=["starter", "played_value"], descending=[True, True])
    .drop(["played_value"])
    .pipe(add_player_photo_url)
    .select(["photo_url"] + PLAYERS_STATS_COLUMNS)
)

# Display players in tabs
st.header("Player Stats")
tab1, tab2 = st.tabs([home_team_name, away_team_name])

with tab1:
    # Display home team players table
    player_stats_table(
        home_team_players,
        on_select="rerun",
        selection_mode="single-row",
        key="home_team_boxscore",
    )
with tab2:
    # Display away team players table
    player_stats_table(
        away_team_players,
        on_select="rerun",
        selection_mode="single-row",
        key="away_team_boxscore",
    )

# Handle player selection from both dataframes
home_selection = (
    st.session_state.get("home_team_boxscore", {}).get("selection", {}).get("rows", [])
)
away_selection = (
    st.session_state.get("away_team_boxscore", {}).get("selection", {}).get("rows", [])
)

# Check if players from both teams are selected
if home_selection and away_selection:
    st.warning(
        "Please select only one player at a time. Home team player has been selected."
    )
    # Prioritize home team selection
    selected_player = home_team_players.row(home_selection[0], named=True).get(
        "player_name"
    )
    st.session_state["selected_player"] = selected_player
    selected_player_id = players_data_raw.filter(
        pl.col("player_name") == selected_player
    ).item(0, "player_id")
    st.session_state["selected_player_id"] = selected_player_id
elif home_selection:
    selected_player = home_team_players.row(home_selection[0], named=True).get(
        "player_name"
    )
    selected_player_id = players_data_raw.filter(
        pl.col("player_name") == selected_player
    ).item(0, "player_id")
    st.session_state["selected_player"] = selected_player
    st.session_state["selected_player_id"] = selected_player_id

    # Show button to view player profile
    if st.button(f"View {selected_player}'s Profile"):
        st.switch_page("pages/player_stats.py")
elif away_selection:
    selected_player = away_team_players.row(away_selection[0], named=True).get(
        "player_name"
    )
    selected_player_id = players_data_raw.filter(
        pl.col("player_name") == selected_player
    ).item(0, "player_id")
    st.session_state["selected_player"] = selected_player
    st.session_state["selected_player_id"] = selected_player_id

    # Show button to view player profile
    if st.button(f"View {selected_player}'s Profile"):
        st.switch_page("pages/player_stats.py")
else:
    st.session_state["selected_player"] = None
    st.session_state["selected_player_id"] = None

# Add button to go back to games list
if st.button("Back to Games List"):
    st.switch_page("pages/games_list.py")
