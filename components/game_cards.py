"""
Game Card Components
Components for displaying game cards and game-related UI elements.
"""

import streamlit as st
from typing import Any
from datetime import datetime
import polars as pl

from utils.app_state import AppState


def game_card(game: dict[str, Any], key_prefix: str = ""):
    """
    Display a game card with team names, scores, and a details button.

    Args:
        game: Game data dictionary
        key_prefix: Optional prefix for element keys
    """
    # Game card styling
    with st.container(border=True):
        # Game type/remarks
        if game.get("game_type") == "playoffs":
            st.caption("Playoffs")
        if game.get("game_remarks") is not None:
            st.caption(game["game_remarks"].title())

        # Teams and scores
        home_team = game.get("home_team", "")
        away_team = game.get("away_team", "")

        col1, col2 = st.columns([5, 2])
        with col1:
            st.write(f"**{away_team}** @ **{home_team}**")
        with col2:
            if (
                game.get("home_team_pts") is not None
                and game.get("away_team_pts") is not None
            ):
                st.write(f"{game['away_team_pts']}-{game['home_team_pts']}")

        # View details button
        if st.button("View Details", key=f"{key_prefix}game_{game.get('id', '')}"):
            AppState.set_selected_game(
                {
                    "id": game.get("id"),
                    "home_team": home_team,
                    "away_team": away_team,
                }
            )
            st.switch_page("pages/game_details.py")


def games_calendar_view(
    games_df, dates_df, current_page: int, dates_per_page: int = 10
):
    """
    Display games in a calendar view grouped by date.

    Args:
        games_df: DataFrame with games data
        dates_df: DataFrame with unique dates
        current_page: Current page index
        dates_per_page: Number of dates to display per page
    """
    if dates_df.is_empty():
        st.info("No games found matching your filters.")
        return

    # Calculate pagination
    total_dates = len(dates_df)
    total_pages = (total_dates + dates_per_page - 1) // dates_per_page

    # Reset page if it's out of bounds
    if current_page >= total_pages or current_page < 0:
        current_page = 0
        st.session_state["games_list_page"] = 0

    # Pagination controls
    if total_pages > 1:
        col1, col2, col3 = st.columns(
            [2, 2, 0.4], gap="large", vertical_alignment="center"
        )

        with col1:
            if st.button("⬅️ Previous", disabled=(current_page <= 0)):
                st.session_state["games_list_page"] = current_page - 1
                st.rerun()

        with col2:
            st.write(f"Page {current_page + 1} of {total_pages}")

        with col3:
            if st.button("Next ➡️", disabled=(current_page >= total_pages - 1)):
                st.session_state["games_list_page"] = current_page + 1
                st.rerun()

    # Calculate start and end indices for the current page
    start_idx = current_page * dates_per_page
    end_idx = min(start_idx + dates_per_page, total_dates)

    # Get dates for current page
    current_page_dates = dates_df.slice(start_idx, end_idx - start_idx)

    for _, row in enumerate(current_page_dates.iter_rows(named=True)):
        date_str = row["date_str"]
        date_games = games_df.filter(pl.col("date_str") == date_str)

        # Format date header
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        st.subheader(date_obj.strftime("%A, %B %d, %Y"))

        # Create game cards grid
        cols = st.columns(min(3, len(date_games)))

        for i, game in enumerate(date_games.iter_rows(named=True)):
            col_idx = i % len(cols)

            with cols[col_idx]:
                game_card(game, key_prefix=f"cal_{i}_")


def games_table_view(games_df: pl.DataFrame):
    """
    Display games in a table view.

    Args:
        games_df: DataFrame with games data
    """
    if games_df.is_empty():
        st.info("No games found matching your filters.")
        return

    # Ensure we have the ID column available for selection
    if "id" not in games_df.columns:
        st.error("Game ID column missing. Cannot enable selection.")
        display_columns = [
            "date",
            "away_team",
            "home_team",
            "away_team_pts",
            "home_team_pts",
            "game_type",
            "arena_name",
        ]
    else:
        display_columns = [
            "date",
            "away_team",
            "home_team",
            "away_team_pts",
            "home_team_pts",
            "game_type",
            "arena_name",
            "id",  # Include ID for selection
        ]

    # Select available columns
    available_columns = [col for col in display_columns if col in games_df.columns]

    # Format game type column
    display_df = games_df.select(available_columns).with_columns(
        pl.col("game_type").str.to_titlecase().name.keep()
    )

    # Display with selection capability
    st.dataframe(
        display_df,
        use_container_width=True,
        column_config={
            "date": st.column_config.DateColumn("Date"),
            "away_team": st.column_config.TextColumn("Away"),
            "home_team": st.column_config.TextColumn("Home"),
            "away_team_pts": st.column_config.NumberColumn("Away Pts"),
            "home_team_pts": st.column_config.NumberColumn("Home Pts"),
            "game_type": st.column_config.TextColumn("Type"),
            "arena_name": st.column_config.TextColumn("Arena"),
            "id": st.column_config.Column("ID", disabled=True, required=False)
            if "id" in available_columns
            else None,
        },
        on_select="rerun",
        key="games_table",
        selection_mode="single-row",
        hide_index=True,
    )

    # Handle row selection
    selected_rows = (
        st.session_state.get("games_table", {}).get("selection", {}).get("rows", [])
    )
    if selected_rows:
        selected_game = games_df.row(selected_rows[0], named=True)
        AppState.set_selected_game(
            {
                "id": selected_game["id"],
                "home_team": selected_game["home_team"],
                "away_team": selected_game["away_team"],
            }
        )
        st.switch_page("pages/game_details.py")


def totals_card(
    total_games: int,
    total_points: int,
    total_assists: int,
    total_rebounds: int,
    total_fg: int,
    total_fga: int,
    total_2p: int,
    total_2pa: int,
    total_3p: int,
    total_3pa: int,
    total_ft: int,
    total_fta: int,
    wins: int,
    losses: int,
) -> None:
    """
    Display career/season totals for points, rebounds, assists, and shooting percentages.

    Args:
        total_games: Total number of games played
        total_points: Total points scored
        total_assists: Total assists made
        total_rebounds: Total rebounds made
        total_fg: Total field goals made
        total_fga: Total field goals attempted
        total_2p: Total two-point field goals made
        total_2pa: Total two-point field goals attempted
        total_3p: Total three-point field goals made
        total_3pa: Total three-point field goals attempted
        total_ft: Total free throws made
        total_fta: Total free throws attempted
        wins: Number of wins
        losses: Number of losses

    Returns:
        None
    """

    st.markdown(f"**Games:** {total_games}")
    st.markdown(f"**Record:** {wins}-{losses}")
    st.markdown(f"**Points:** {total_points}")
    st.markdown(f"**Rebounds:** {total_rebounds}")
    st.markdown(f"**Assists:** {total_assists}")
    st.markdown(
        f"**FG:** {total_fg}/{total_fga} ({total_fg / total_fga * 100:.1f}%)"
        if total_fga > 0
        else "**FG:** 0/0 (0.0%)"
    )
    st.markdown(
        f"**2P:** {total_2p}/{total_2pa} ({total_2p / total_2pa * 100:.1f}%)"
        if total_2pa > 0
        else "**2P:** 0/0 (0.0%)"
    )
    st.markdown(
        f"**3P:** {total_3p}/{total_3pa} ({total_3p / total_3pa * 100:.1f}%)"
        if total_3pa > 0
        else "**3P:** 0/0 (0.0%)"
    )
    st.markdown(
        f"**FT:** {total_ft}/{total_fta} ({total_ft / total_fta * 100:.1f}%)"
        if total_fta > 0
        else "**FT:** 0/0 (0.0%)"
    )


def highs_card(
    points_high: int,
    rebounds_high: int,
    assists_high: int,
    fg_high: int,
    fg3_high: int,
    high_points_game: pl.DataFrame,
    high_rebounds_game: pl.DataFrame,
    high_assists_game: pl.DataFrame,
    high_fg_game: pl.DataFrame,
    high_fg3_game: pl.DataFrame,
) -> None:
    """

    Display career highs for points, rebounds, assists, and field goals.

    Args:
        points_high: Career or season high points
        rebounds_high: Career or season high rebounds
        assists_high: Career or season high assists
        fg_high: Career or season high field goals made
        fg3_high: Career or season high three-pointers made
        high_points_game: DataFrame with game details for high points
        high_rebounds_game: DataFrame with game details for high rebounds
        high_assists_game: DataFrame with game details for high assists
        high_fg_game: DataFrame with game details for high field goals
        high_fg3_game: DataFrame with game details for high three-pointers

    Returns:
        None

    """
    st.markdown(
        f"**Points:** {points_high} ({high_points_game.item(row=0, column='date').strftime('%Y-%m-%d')} vs {high_points_game.item(row=0, column='opponent')})"
    )
    st.markdown(
        f"**Rebounds:** {rebounds_high} ({high_rebounds_game.item(row=0, column='date').strftime('%Y-%m-%d')} vs {high_rebounds_game.item(row=0, column='opponent')})"
    )
    st.markdown(
        f"**Assists:** {assists_high} ({high_assists_game.item(row=0, column='date').strftime('%Y-%m-%d')} vs {high_assists_game.item(row=0, column='opponent')})"
    )
    st.markdown(
        f"**FG Made:** {fg_high} ({high_fg_game.item(row=0, column='date').strftime('%Y-%m-%d')} vs {high_fg_game.item(row=0, column='opponent')})"
    )
    st.markdown(
        f"**3P Made:** {fg3_high} ({high_fg3_game.item(row=0, column='date').strftime('%Y-%m-%d')} vs {high_fg3_game.item(row=0, column='opponent')})"
    )
