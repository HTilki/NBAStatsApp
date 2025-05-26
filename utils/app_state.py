"""
App State Module
Manages application state and session variables.
"""

import streamlit as st
from typing import Dict, Any, Optional, TypeVar

from utils.connection import get_connection
from data.queries import get_teams_list, get_seasons_list

T = TypeVar("T")


class AppState:
    """
    Singleton class to manage application state consistently across pages.
    Handles initialization of common session state variables and provides
    helper methods for state management.
    """

    @staticmethod
    def initialize_core_state():
        """
        Initialize core application state variables that should be available
        across all pages (teams list, seasons list, etc.)
        """
        # Load teams and seasons data if not already in session state
        if "teams" not in st.session_state or "seasons" not in st.session_state:
            conn = get_connection()
            if "teams" not in st.session_state:
                st.session_state["teams"] = get_teams_list(conn)
            if "seasons" not in st.session_state:
                st.session_state["seasons"] = get_seasons_list(conn)
            conn.close()

        # Initialize selected_game if not present
        if "selected_game" not in st.session_state:
            st.session_state["selected_game"] = None

    @staticmethod
    def initialize_pagination(key: str = "current_page"):
        """
        Initialize pagination state for a specific key.

        Args:
            key: Session state key for pagination
        """
        if key not in st.session_state:
            st.session_state[key] = 0

    @staticmethod
    def set_selected_game(game_data: Dict[str, Any]):
        """
        Set the selected game in session state and navigate to game details page.

        Args:
            game_data: Game data dictionary
        """
        st.session_state["selected_game"] = game_data
        # st.rerun()  # This will trigger a page reload with the updated state

    @staticmethod
    def set_selected_team(team_name: str):
        """
        Set the selected player in session state and navigate to player profile page.

        Args:
            player_name: Player name
            player_id: Optional player ID
        """
        st.session_state["selected_team"] = team_name
        # st.rerun()  # This will trigger a page reload with the updated state

    @staticmethod
    def set_selected_player(player_name: str, player_id: Optional[int] = None):
        """
        Set the selected player in session state and navigate to player profile page.

        Args:
            player_name: Player name
            player_id: Optional player ID
        """
        st.session_state["selected_player"] = player_name
        if player_id:
            st.session_state["selected_player_id"] = player_id
        st.rerun()  # This will trigger a page reload with the updated state

    @staticmethod
    def get_or_create(key: str, default_value: T) -> T:
        """
        Get a value from session state or create it with a default value if it doesn't exist.

        Args:
            key: Session state key
            default_value: Default value to use if key doesn't exist

        Returns:
            Value from session state
        """
        if key not in st.session_state:
            st.session_state[key] = default_value
        return st.session_state[key]

    @staticmethod
    def clear(key: str):
        """
        Clear a specific key from session state.

        Args:
            key: Session state key to clear
        """
        if key in st.session_state:
            del st.session_state[key]
