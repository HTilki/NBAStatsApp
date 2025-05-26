"""
Table Components
Reusable table components for the NBA Stats app.
"""

import streamlit as st
import polars as pl
from typing import Any, Optional

from data.column_config import PLAYERS_COLUMN_CONFIG, TEAM_COLUMN_CONFIG


def stats_table(
    df: pl.DataFrame,
    column_config: dict[str, Any] = None,
    height: Optional[int] = None,
    hide_index: bool = True,
    use_container_width: bool = True,
    **kwargs: Any,
):
    """
    Display a formatted statistics table.

    Args:
        df: Polars DataFrame with statistics data
        column_config: Optional column configuration dictionary
        height: Optional height for the table
        hide_index: Whether to hide the index column (default True)
        use_container_width: Whether to use the full container width (default True)
    """
    if df.is_empty():
        st.info("No data available.")
        return

    # Display with the appropriate configuration
    st.dataframe(
        df,
        column_config=column_config,
        height=height,
        hide_index=hide_index,
        use_container_width=use_container_width,
        **kwargs,
    )


def player_stats_table(
    df: pl.DataFrame,
    height: Optional[int] = None,
    custom_config: Optional[dict[str, Any]] = None,
    **kwargs: Any,
):
    """
    Display a formatted player statistics table.

    Args:
        df: Polars DataFrame with player statistics
        height: Optional height for the table
        custom_config: Optional custom column configuration to override defaults
    """
    if df.is_empty():
        st.info("No player statistics available.")
        return

    # Use the default player column config and override with any custom config
    config = PLAYERS_COLUMN_CONFIG.copy()
    if custom_config:
        config.update(custom_config)

    stats_table(df, column_config=config, height=height, **kwargs)


def team_stats_table(
    df: pl.DataFrame,
    height: Optional[int] = None,
    custom_config: Optional[dict[str, Any]] = None,
    **kwargs: Any,
):
    """
    Display a formatted team statistics table.

    Args:
        df: Polars DataFrame with team statistics
        height: Optional height for the table
        custom_config: Optional custom column configuration to override defaults
    """
    if df.is_empty():
        st.info("No team statistics available.")
        return

    # Use the default team column config and override with any custom config
    config = TEAM_COLUMN_CONFIG.copy()
    if custom_config:
        config.update(custom_config)

    stats_table(df, column_config=config, height=height, **kwargs)


def pagination_controls(
    total_items: int, items_per_page: int, current_page_key: str = "current_page"
) -> int:
    """
    Display pagination controls and manage pagination state.

    Args:
        total_items: Total number of items to paginate
        items_per_page: Number of items per page
        current_page_key: Session state key for the current page

    Returns:
        Current page index
    """
    # Initialize session state if needed
    if current_page_key not in st.session_state:
        st.session_state[current_page_key] = 0

    # Calculate total pages
    total_pages = (total_items + items_per_page - 1) // items_per_page

    # Reset page if out of bounds
    if (
        st.session_state[current_page_key] >= total_pages
        or st.session_state[current_page_key] < 0
    ):
        st.session_state[current_page_key] = 0

    # Navigation buttons
    col1, col2, col3, col4 = st.columns([1, 3, 3, 1])

    with col1:
        if st.button("<<", key=f"{current_page_key}_first"):
            st.session_state[current_page_key] = 0
            st.rerun()

    with col2:
        if st.button("Previous", key=f"{current_page_key}_prev"):
            st.session_state[current_page_key] = max(
                0, st.session_state[current_page_key] - 1
            )
            st.rerun()

    with col3:
        if st.button("Next", key=f"{current_page_key}_next"):
            st.session_state[current_page_key] = min(
                total_pages - 1, st.session_state[current_page_key] + 1
            )
            st.rerun()

    with col4:
        if st.button(">>", key=f"{current_page_key}_last"):
            st.session_state[current_page_key] = total_pages - 1
            st.rerun()

    # Page indicator
    st.caption(f"Page {st.session_state[current_page_key] + 1} of {total_pages}")

    return st.session_state[current_page_key]
