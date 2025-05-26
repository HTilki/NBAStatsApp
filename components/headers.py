"""
Header Components
Reusable header and title components for the NBA Stats app.
"""

import streamlit as st
from typing import Optional


def page_header(title: str, subtitle: Optional[str] = None, icon: Optional[str] = None):
    """
    Display a consistent page header with title and optional subtitle.

    Args:
        title: Main page title
        subtitle: Optional subtitle text
        icon: Optional emoji icon
    """
    if icon:
        st.title(f"{icon} {title}")
    else:
        st.title(title)

    if subtitle:
        st.caption(subtitle)


def team_matchup_header(
    home_team: str,
    away_team: str,
    home_score: Optional[int] = None,
    away_score: Optional[int] = None,
    game_date: Optional[str] = None,
):
    """
    Display a game matchup header with team names and optional scores.

    Args:
        home_team: Home team name
        away_team: Away team name
        home_score: Optional home team score
        away_score: Optional away team score
        game_date: Optional game date string
    """
    col1, col2, col3 = st.columns(spec=[1, 0.2, 1])

    with col1:
        st.markdown(
            f"<h3 style='text-align: right;'>{away_team}</h3>", unsafe_allow_html=True
        )

    with col2:
        if home_score is not None and away_score is not None:
            st.markdown(
                f"<h3 style='text-align: center;'>{away_score} - {home_score}</h3>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<h3 style='text-align: center;'>@</h3>", unsafe_allow_html=True
            )

    with col3:
        st.markdown(
            f"<h3 style='text-align: left;'>{home_team}</h3>", unsafe_allow_html=True
        )

    if game_date:
        st.caption(f"Game Date: {game_date}")


def player_header(
    name: str, player_id: Optional[int] = None, team: Optional[str] = None
):
    """
    Display a player header with photo and name.

    Args:
        name: Player name
        player_id: Optional player ID to fetch photo
        team: Optional team name
    """
    from utils.players import get_player_photo_url

    img_col, name_col, _ = st.columns(spec=[0.5, 1, 3], gap="small")

    if player_id:
        photo_url = get_player_photo_url(player_id)
        with img_col:
            st.image(photo_url, width=150)

    with name_col:
        st.header(name)
        if team:
            st.caption(f"Team: {team}")


def team_header(
    name: str, team_abbreviation: Optional[str] = None, season: Optional[str] = None
):
    """
    Display a team header with logo and name.

    Args:
        name: Team name
        team_abbreviation: Team abbreviation for logo
        season: Optional season to display
    """
    from utils.teams import get_team_logo_url

    img_col, name_col, _ = st.columns(spec=[0.5, 1, 3], gap="small")

    if team_abbreviation:
        logo_url = get_team_logo_url(team_abbreviation)
        with img_col:
            st.image(logo_url, width=150)

    with name_col:
        st.header(name)
        if season:
            st.caption(f"Season: {season}")
