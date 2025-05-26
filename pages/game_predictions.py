"""
Game Predictions Page
Displays predictions for upcoming NBA games with win probabilities.
"""

import streamlit as st
import polars as pl
import json
from datetime import datetime
from pathlib import Path

from utils.connection import get_connection
from utils.teams import get_team_logo_url, get_abbreviation
from data.queries import get_teams_list

# Set page config
# st.set_page_config(layout="wide")

# Initialize session state for teams if not exists
if "teams" not in st.session_state:
    conn = get_connection()
    st.session_state["teams"] = get_teams_list(conn)
    conn.close()

# Page title
st.title("Game Predictions")


# Function to load prediction data
def load_prediction_data():
    """Load prediction data from JSON file or API"""
    # In a real app, you might fetch this from an API or database
    # For now, we'll use a static JSON file path
    predictions_dir = Path(__file__).parent.parent / "data" / "predictions"

    try:
        # For now, check the name of files in the directory
        predictions_files = list(predictions_dir.glob("*.json"))

        # If no files found, return empty data
        if not predictions_files:
            st.warning("No prediction files found.")
            return {"metadata": {"game_count": 0}, "games": []}

        # Load the most recent prediction file
        predictions_file = max(predictions_files, key=lambda x: x.stat().st_mtime)

        # Load the predictions
        with open(predictions_file, "r") as f:
            data = json.load(f)

        return data

    except Exception as e:
        st.error(f"Error loading prediction data: {e}")
        return {"metadata": {"game_count": 0}, "games": []}


# Load prediction data
prediction_data = load_prediction_data()

# Display metadata about the predictions
metadata = prediction_data.get("metadata", {})
if metadata:
    st.sidebar.subheader("Prediction Metadata")
    st.sidebar.write(f"**Generated:** {metadata.get('generated_at', 'N/A')}")
    st.sidebar.write(f"**Model:** {metadata.get('model', 'N/A')}")
    st.sidebar.write(f"**Version:** {metadata.get('version', 'N/A')}")
    # TODO fix / st.sidebar.write(f"**Game Count:** {metadata.get('game_count', 0)}")

# Get all games and find the next matchup for each unique team pair
games = prediction_data.get("games", [])

# Find the next upcoming matchup (closest to current date)
# Sort games by date
today = datetime.now().strftime("%Y-%m-%d")
upcoming_games = sorted(games, key=lambda x: x["date"])

# Find first game after today
next_game = None
for game in upcoming_games:
    if game["date"] >= today:
        next_game = game
        break

# If no next game found, show a message
if next_game is None:
    st.info("No upcoming games with predictions available.")
else:
    # Display the next matchup
    st.header("Next Matchup")

    # Get game information
    home_team = next_game["teams"]["home"]
    away_team = next_game["teams"]["away"]

    # Format date
    try:
        game_date = datetime.strptime(next_game["date"], "%Y-%m-%d")
        date_str = game_date.strftime("%A, %B %d, %Y")
    except Exception:
        date_str = next_game["date"]

    # Display date
    st.subheader(f"{date_str}")

    # Create a container for the matchup
    with st.container(border=True):
        # Create columns for team names and logos
        col1, col2, col3 = st.columns([2, 1, 2])

        # Get team logos
        home_logo_url = get_team_logo_url(home_team["abbreviation"])
        away_logo_url = get_team_logo_url(away_team["abbreviation"])

        # Away team (left side)
        with col1:
            st.image(away_logo_url, width=100)
            st.markdown(f"### {away_team['name']}")
            st.metric("Win Probability", f"{away_team['win_probability']:.1%}")

        # VS in the middle
        with col2:
            st.markdown("### VS")

        # Home team (right side)
        with col3:
            st.image(home_logo_url, width=100)
            st.markdown(f"### {home_team['name']}")
            st.metric("Win Probability", f"{home_team['win_probability']:.1%}")

        # Visualization of win probabilities
        # st.subheader("Win Probability Comparison")
        # add stats here

        # Display matchup stats if available
        if "matchup_stats" in next_game:
            st.subheader("Head to Head Stats")

            matchup = next_game["matchup_stats"]
            cols_stats = st.columns(3)
            with cols_stats[0]:
                st.metric("Previous Games", matchup.get("h2h_games_played", "N/A"))
            with cols_stats[1]:
                h2h_pct = matchup.get("h2h_win_pct", 0)
                st.metric(f"{home_team['abbreviation']} Win %", f"{h2h_pct:.0%}")
            with cols_stats[2]:
                days = matchup.get("days_since_last_matchup", "N/A")
                st.metric("Last Played", f"{days} days ago")

# Add a way to see all predictions in a table if desired
with st.expander("View Upcoming Game Predictions"):
    # Convert the games to a dataframe for display
    table_data = []
    for game in games:
        home_team = game["teams"]["home"]
        away_team = game["teams"]["away"]
        winning_team_abbreviation = get_abbreviation(
            teams=st.session_state["teams"], team_name=game["prediction"]["winner_name"]
        )

        table_data.append(
            {
                "date": game["date"],
                "home_team": home_team["name"],
                "away_team": away_team["name"],
                "home_win_prob": home_team["win_probability"] * 100,
                "away_win_prob": away_team["win_probability"] * 100,
                "predicted_winner": get_team_logo_url(
                    team_abbreviation=winning_team_abbreviation
                )
                if "prediction" in game
                else "N/A",
            }
        )

    # Convert to DataFrame
    games_df = (
        pl.DataFrame(table_data)
        .sort("date")
        .unique(subset=["home_team", "away_team"], keep="first", maintain_order=True)
    )

    # Display as dataframe
    st.dataframe(
        games_df,
        use_container_width=True,
        column_config={
            "date": st.column_config.DateColumn("Date"),
            "home_team": st.column_config.TextColumn("Home"),
            "away_team": st.column_config.TextColumn("Away"),
            "home_win_prob": st.column_config.ProgressColumn(
                "Home Win %", format="%.1f%%", min_value=0, max_value=100
            ),
            "away_win_prob": st.column_config.ProgressColumn(
                "Away Win %", format="%.1f%%", min_value=0, max_value=100
            ),
            "predicted_winner": st.column_config.ImageColumn("Predicted Winner"),
        },
        hide_index=True,
    )


# Add explanation about the prediction model
with st.expander("About the Prediction Model"):
    st.write("""
    ### How These Predictions Work
    
    The predictions displayed on this page are generated using a machine learning model trained on historical NBA game data. The model takes into account factors such as:
    
    - Team performance statistics (scoring, rebounding, assists, etc.)
    - Recent form (win/loss trends)
    - Head-to-head matchup history
    - Home court advantage
    
    The win probability percentages indicate the model's confidence in each team winning the upcoming matchup. Higher percentages indicate greater confidence.
    
    **Note**: These predictions are for informational purposes only and should not be used for betting or other financial decisions.
    """)
