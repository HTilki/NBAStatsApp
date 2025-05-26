"""
Filter Components
Reusable filter components for the NBA Stats app.
"""

import streamlit as st
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime


def season_filter(
    seasons: List[str],
    default_index: int = 0,
    key_prefix: str = "",
    sidebar: bool = False,
) -> str:
    """
    Display a season filter dropdown.

    Args:
        seasons: List of season options (e.g., ["2022-23", "2021-22"])
        default_index: Default selected index
        key_prefix: Optional prefix for session state key
        sidebar: Whether to display in the sidebar (default False)

    Returns:
        Selected season
    """
    key = f"{key_prefix}selected_season" if key_prefix else "selected_season"
    if sidebar:
        return st.sidebar.selectbox(
            "Select Season", options=seasons, index=default_index, key=key
        )
    else:
        return st.selectbox(
            "Select Season", options=seasons, index=default_index, key=key
        )


def team_filter(
    teams: List[Dict[str, Any]],
    include_all: bool = True,
    key_prefix: str = "",
    sidebar: bool = False,
) -> str:
    """
    Display a team filter dropdown.

    Args:
        teams: List of team dictionaries
        include_all: Whether to include an "All Teams" option
        key_prefix: Optional prefix for session state key
        sidebar: Whether to display in the sidebar (default False)

    Returns:
        Selected team name
    """
    key = f"{key_prefix}selected_team" if key_prefix else "selected_team"
    team_options = (
        ["All Teams"] + [team["name"] for team in teams]
        if include_all
        else [team["name"] for team in teams]
    )
    if sidebar:
        return st.sidebar.selectbox("Team", options=team_options, key=key)
    else:
        return st.selectbox("Team", options=team_options, key=key)


def game_type_filter(key_prefix: str = "", sidebar: bool = False) -> str:
    """
    Display a game type filter dropdown.

    Args:
        key_prefix: Optional prefix for session state key
        sidebar: Whether to display in the sidebar (default False)

    Returns:
        Selected game type
    """
    key = f"{key_prefix}selected_game_type" if key_prefix else "selected_game_type"
    game_types = {
        "all": "All Games",
        "regular season": "Regular Season",
        "playoffs": "Playoffs",
        "in-season tournament": "In-Season Tournament",
        "play-in": "Play-In Games",
    }
    if sidebar:
        return st.sidebar.selectbox(
            "Game Type",
            options=game_types.keys(),
            format_func=lambda x: game_types[x],
            key=key,
        )
    else:
        return st.selectbox(
            "Game Type",
            options=game_types.keys(),
            format_func=lambda x: game_types[x],
            key=key,
        )


def date_range_filter(
    start_year: int,
    end_date: datetime = None,
    key_prefix: str = "",
    sidebar: bool = False,
) -> Tuple[datetime, datetime]:
    """
    Display a date range filter with two date input fields.

    Args:
        start_year: Year to use for the default start date
        end_date: Default end date (defaults to today if None)
        key_prefix: Optional prefix for session state key
        sidebar: Whether to display in the sidebar (default False)

    Returns:
        Tuple of (start_date, end_date)
    """
    if end_date is None:
        end_date = datetime.now()

    start_key = f"{key_prefix}start_date" if key_prefix else "start_date"
    end_key = f"{key_prefix}end_date" if key_prefix else "end_date"
    if sidebar:
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_date = st.sidebar.date_input(
                "From Date", value=datetime(start_year, 6, 1), key=start_key
            )
        with col2:
            end_date = st.sidebar.date_input("To Date", value=end_date, key=end_key)

        return start_date, end_date
    else:
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "From Date", value=datetime(start_year, 6, 1), key=start_key
            )
        with col2:
            end_date = st.date_input("To Date", value=end_date, key=end_key)

        return start_date, end_date


def player_search_filter(
    label: str = "Search for a player",
    default: str = "",
    key_prefix: str = "",
    sidebar: bool = False,
) -> str:
    """
    Display a player search text input.

    Args:
        label: Label for the text input
        default: Default value
        key_prefix: Optional prefix for session state key
        sidebar: Whether to display in the sidebar (default False)

    Returns:
        Player name entered by the user
    """

    key = f"{key_prefix}player_search" if key_prefix else "player_search"
    if sidebar:
        return st.sidebar.text_input(label, value=default, key=key)
    else:
        return st.text_input(label, value=default, key=key)


def metric_selector(
    key_prefix: str = "", sidebar: bool = False
) -> Tuple[str, str, bool]:
    """
    Display a metric selector dropdown for player or team charts.

    Args:
        key_prefix: Optional prefix for session state key
        sidebar: Whether to display in the sidebar (default False)

    Returns:
        Tuple of (metric_key, metric_name, is_percentage)
    """
    key = f"{key_prefix}selected_metric" if key_prefix else "selected_metric"

    metric_options = {
        "points": "Points",
        "rebounds": "Rebounds",
        "assists": "Assists",
        "steals": "Steals",
        "blocks": "Blocks",
        "plus_minus": "Plus/Minus",
        "turnovers": "Turnovers",
        "made_field_goal": "FG Made",
        "attempted_field_goal": "FG Attempted",
        "field_goal_percent": "Field Goal %",
        "attempted_three_point": "3P Attempted",
        "made_three_point": "3P Made",
        "three_point_percent": "Three Point %",
        "attempted_free_throw": "FT Attempted",
        "made_free_throw": "FT Made",
        "free_throw_percent": "Free Throw %",
        "attempted_two_point": "2P Attempted",
        "made_two_point": "2P Made",
        "two_point_percent": "Two Point %",
    }
    if sidebar:
        selected_metric = st.sidebar.selectbox(
            "Select Metric",
            options=list(metric_options.keys()),
            format_func=lambda x: metric_options[x],
            key=key,
        )
    else:
        selected_metric = st.selectbox(
            "Select Metric",
            options=list(metric_options.keys()),
            format_func=lambda x: metric_options[x],
            key=key,
        )

    # Determine if the selected metric is a percentage
    is_percentage = selected_metric in [
        "field_goal_percent",
        "two_point_percent",
        "three_point_percent",
        "free_throw_percent",
        "fg_pct",
        "2p_pct",
        "3p_pct",
        "ft_pct",
    ]

    metric_name = metric_options[selected_metric]

    return selected_metric, metric_name, is_percentage


def filters_sidebar(
    title: str = "Filters",
    seasons: Optional[List[str]] = None,
    teams: Optional[List[Dict[str, Any]]] = None,
    include_game_type: bool = True,
    include_date_range: bool = True,
    start_year: Optional[int] = None,
    key_prefix: str = "",
) -> Dict[str, Any]:
    """
    Display a complete sidebar with common filters.

    Args:
        title: Title for the sidebar
        seasons: List of season options
        teams: List of team dictionaries
        include_game_type: Whether to include game type filter
        include_date_range: Whether to include date range filter
        start_year: Year to use for date range start (required if include_date_range is True)
        key_prefix: Optional prefix for session state keys

    Returns:
        Dictionary of filter values
    """
    st.sidebar.header(title)

    filters = {}

    # Season filter
    if seasons:
        selected_season = season_filter(seasons, key_prefix=key_prefix, sidebar=True)
        filters["season"] = selected_season
        if start_year is None and include_date_range:
            start_year = int(selected_season.split("-")[0])

    # Game type filter
    if include_game_type:
        selected_game_type = game_type_filter(key_prefix=key_prefix, sidebar=True)
        if selected_game_type != "all":
            filters["game_type"] = selected_game_type

    # Team filter
    if teams:
        selected_team = team_filter(teams, key_prefix=key_prefix, sidebar=True)
        if selected_team != "All Teams":
            filters["team"] = selected_team

    # Date range filter
    if include_date_range:
        if start_year is None:
            start_year = datetime.now().year - 1

        start_date, end_date = date_range_filter(
            start_year, key_prefix=key_prefix, sidebar=True
        )
        if start_date:
            filters["date_from"] = start_date
        if end_date:
            filters["date_to"] = end_date

    return filters


def opponent_filter(
    opponents: list[str], key_prefix: str = "", sidebar: bool = False
) -> str:
    """
    Display a opponent filter dropdown.

    Args:
        opponents: List of opponent options
        key_prefix: Optional prefix for session state key
        sidebar: Whether to display in the sidebar (default False)

    Returns:
        Selected opponent
    """
    if "All Teams" not in opponents:
        opponents = ["All Teams"] + opponents
    key = f"{key_prefix}selected_opponent" if key_prefix else "selected_opponent"
    if sidebar:
        return st.sidebar.selectbox("Select Opponent", options=opponents, key=key)
    else:
        return st.selectbox("Select Opponent", options=opponents, key=key)
