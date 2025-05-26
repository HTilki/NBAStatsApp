"""
NBA Game Statistics Viewer
Main entry point for the Streamlit application that displays NBA game statistics.
"""

import streamlit as st

# Configure the page
st.set_page_config(
    page_title="NBA Stats",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Set up navigation
pg = st.navigation(
    [
        st.Page("pages/games_list.py", title="Games", icon="📅"),
        st.Page("pages/game_details.py", title="Game Stats", icon="📊"),
        st.Page("pages/player_stats.py", title="Player Stats", icon="👤"),
        st.Page("pages/team_stats.py", title="Team Stats", icon="🏆"),
        st.Page("pages/season_stats.py", title="Season Stats", icon="📈"),
        st.Page("pages/game_predictions.py", title="Game Predictions", icon="🔮"),
    ]
)

pg.run()
