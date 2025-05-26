"""
Layout Components
Reusable layout components and patterns for the NBA Stats app.
"""

import streamlit as st
from typing import List, Dict, Any, Optional, Callable
import polars as pl


def two_column_layout(
    left_content: Callable,
    right_content: Callable,
    left_width: int = 1,
    right_width: int = 1,
    gap: str = "small",
):
    """
    Create a two-column layout with custom content in each column.

    Args:
        left_content: Function that renders content in the left column
        right_content: Function that renders content in the right column
        left_width: Relative width of left column
        right_width: Relative width of right column
        gap: Gap size between columns ("small", "medium", "large")
    """
    cols = st.columns(spec=[left_width, right_width], gap=gap)

    with cols[0]:
        left_content()

    with cols[1]:
        right_content()


def tabbed_interface(tabs_dict: Dict[str, Callable], default_tab: Optional[str] = None):
    """
    Create a tabbed interface with custom content in each tab.

    Args:
        tabs_dict: Dictionary mapping tab names to content functions
        default_tab: Optional default tab to select
    """
    tab_names = list(tabs_dict.keys())

    # Create tabs
    tabs = st.tabs(tab_names)

    # Render content in each tab
    for i, tab_name in enumerate(tab_names):
        with tabs[i]:
            tabs_dict[tab_name]()


def calendar_layout(
    dates_df: pl.DataFrame,
    games_df: pl.DataFrame,
    date_col: str = "date",
    date_str_col: str = "date_str",
    current_page: int = 0,
    dates_per_page: int = 10,
    game_renderer: Callable[[pl.DataFrame], None] = None,
):
    """
    Create a calendar-style layout for games grouped by date.

    Args:
        dates_df: DataFrame with unique dates
        games_df: DataFrame with games data
        date_col: Column name for date values
        date_str_col: Column name for date string representation
        current_page: Current page index for pagination
        dates_per_page: Number of dates to display per page
        game_renderer: Function to render each game
    """
    if dates_df.is_empty() or games_df.is_empty():
        st.info("No games found.")
        return

    # Calculate pagination
    total_dates = len(dates_df)
    start_idx = current_page * dates_per_page
    end_idx = min(start_idx + dates_per_page, total_dates)

    # Get dates for current page
    page_dates = dates_df.slice(start_idx, end_idx - start_idx)

    # Display each date with its games
    for _, date_row in enumerate(page_dates.to_dicts()):
        date_val = date_row[date_col]
        date_str = date_row[date_str_col]

        # Get games for this date
        date_games = games_df.filter(pl.col(date_col) == date_val)

        # Display date header
        st.subheader(date_str)

        # Display games for this date
        if game_renderer:
            game_renderer(date_games)
        else:
            # Default game rendering
            for game in date_games.to_dicts():
                st.markdown(
                    f"{game.get('away_team', '')} @ {game.get('home_team', '')}"
                )


def card_grid(
    items: List[Dict[str, Any]],
    renderer: Callable[[Dict[str, Any]], None],
    columns: int = 3,
    use_container: bool = True,
):
    """
    Create a grid of cards with custom content.

    Args:
        items: List of item dictionaries to render as cards
        renderer: Function to render each item as a card
        columns: Number of columns in the grid
        use_container: Whether to use st.container for cards
    """
    if not items:
        st.info("No items to display.")
        return

    # Create columns
    cols = st.columns(columns)

    # Distribute items into columns
    for i, item in enumerate(items):
        col_idx = i % columns
        with cols[col_idx]:
            if use_container:
                with st.container(border=True):
                    renderer(item)
            else:
                renderer(item)


def expandable_sections(
    sections: Dict[str, Callable], default_expanded: Optional[List[str]] = None
):
    """
    Create expandable sections with custom content.

    Args:
        sections: Dictionary mapping section names to content functions
        default_expanded: List of section names to expand by default
    """
    if default_expanded is None:
        default_expanded = []

    for section_name, content_fn in sections.items():
        with st.expander(section_name, section_name in default_expanded):
            content_fn()
