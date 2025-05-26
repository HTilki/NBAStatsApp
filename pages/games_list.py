"""
Games List Page
Displays a list of NBA games with filtering options.
"""

import streamlit as st

from utils.connection import get_connection
from data.queries import get_game_schedule
from utils.app_state import AppState
from components.headers import page_header
from components.filters import filters_sidebar
from utils.game_processing import prepare_game_result_data
from components.game_cards import games_calendar_view, games_table_view

# Initialize core state (teams, seasons)
AppState.initialize_core_state()

# Initialize pagination state
AppState.initialize_pagination("games_list_page")

# Page header
page_header("NBA Games", icon="📅")

# Apply filters from sidebar
season_year = None
filters = {}
if st.session_state.get("seasons"):
    # Get filter values from sidebar
    filters = filters_sidebar(
        title="Filter Games",
        seasons=st.session_state["seasons"],
        teams=st.session_state["teams"],
        include_game_type=True,
        include_date_range=True,
        key_prefix="games_list_",
    )

    # Extract season year for date calculations if needed
    if "season" in filters:
        season_year = int(filters["season"].split("-")[0])

# Get data
conn = get_connection()
games = get_game_schedule(conn, filters)
conn.close()

# Display games
if games.is_empty():
    st.info("No games found matching your filters.")
else:
    # Process games data
    games_data, dates_data = prepare_game_result_data(
        games, group_by_date=True, sort_desc=True
    )

    # Create tabs for different views
    tab1, tab2 = st.tabs(["Calendar View", "Table View"])
    with tab1:
        # Calendar view grouped by date with pagination
        current_page = st.session_state.get("games_list_page", 0)
        games_calendar_view(games_data, dates_data, current_page)

    with tab2:
        # Table view with all games - using the updated games_table_view that handles selection
        games_table_view(games_data)
