"""
Team Utilities Module
Functions for handling team abbreviations and names.
"""

from typing import Optional, Dict, List, Any
from datetime import date, datetime
import json
from pathlib import Path
from utils.connection import get_connection
import polars as pl

# Team abbreviation history
TEAM_ABBREVIATION_HISTORY = {
    "Atlanta Hawks": {"abbreviation": "ATL", "from": "1969-01-01", "to": None},
    "Boston Celtics": {"abbreviation": "BOS", "from": "1969-01-01", "to": None},
    "Brooklyn Nets": {"abbreviation": "BKN", "from": "2012-01-01", "to": None},
    "New Jersey Nets": {
        "abbreviation": "NJN",
        "from": "1969-01-01",
        "to": "2012-01-01",
    },
    "Charlotte Hornets": {"abbreviation": "CHO", "from": "2014-01-01", "to": None},
    "Charlotte Bobcats": {
        "abbreviation": "CHA",
        "from": "2004-01-01",
        "to": "2014-01-01",
    },
    "Chicago Bulls": {"abbreviation": "CHI", "from": "1969-01-01", "to": None},
    "Cleveland Cavaliers": {"abbreviation": "CLE", "from": "1971-01-01", "to": None},
    "Dallas Mavericks": {"abbreviation": "DAL", "from": "1980-01-01", "to": None},
    "Denver Nuggets": {"abbreviation": "DEN", "from": "1977-01-01", "to": None},
    "Detroit Pistons": {"abbreviation": "DET", "from": "1969-01-01", "to": None},
    "Golden State Warriors": {"abbreviation": "GSW", "from": "1971-01-01", "to": None},
    "Houston Rockets": {"abbreviation": "HOU", "from": "1971-01-01", "to": None},
    "Indiana Pacers": {"abbreviation": "IND", "from": "1976-01-01", "to": None},
    "Kansas City Kings": {
        "abbreviation": "KCK",
        "from": "1975-01-01",
        "to": "1985-01-01",
    },
    "Los Angeles Clippers": {"abbreviation": "LAC", "from": "1984-01-01", "to": None},
    "Los Angeles Lakers": {"abbreviation": "LAL", "from": "1969-01-01", "to": None},
    "Memphis Grizzlies": {"abbreviation": "MEM", "from": "2001-01-01", "to": None},
    "Miami Heat": {"abbreviation": "MIA", "from": "1988-01-01", "to": None},
    "Milwaukee Bucks": {"abbreviation": "MIL", "from": "1969-01-01", "to": None},
    "Minnesota Timberwolves": {"abbreviation": "MIN", "from": "1989-01-01", "to": None},
    "New Orleans Pelicans": {"abbreviation": "NOP", "from": "2013-01-01", "to": None},
    "New Orleans Hornets": {
        "abbreviation": "NOH",
        "from": "2002-01-01",
        "to": "2013-01-01",
    },
    "New Orleans/Oklahoma City Hornets": {
        "abbreviation": "NOK",
        "from": "2005-01-01",
        "to": "2007-01-01",
    },
    "New Orleans Jazz": {
        "abbreviation": "NOJ",
        "from": "1975-01-01",
        "to": "1979-01-01",
    },
    "New York Knicks": {"abbreviation": "NYK", "from": "1969-01-01", "to": None},
    "Oklahoma City Thunder": {"abbreviation": "OKC", "from": "2008-01-01", "to": None},
    "Seattle SuperSonics": {
        "abbreviation": "SEA",
        "from": "1969-01-01",
        "to": "2008-01-01",
    },
    "St. Louis Hawks": {
        "abbreviation": "SLH",
        "from": "1969-01-01",
        "to": "1972-01-01",
    },
    "Orlando Magic": {"abbreviation": "ORL", "from": "1989-01-01", "to": None},
    "Philadelphia 76ers": {"abbreviation": "PHI", "from": "1969-01-01", "to": None},
    "Phoenix Suns": {"abbreviation": "PHX", "from": "1969-01-01", "to": None},
    "Portland Trail Blazers": {"abbreviation": "POR", "from": "1971-01-01", "to": None},
    "Sacramento Kings": {"abbreviation": "SAC", "from": "1985-01-01", "to": None},
    "San Antonio Spurs": {"abbreviation": "SAS", "from": "1976-01-01", "to": None},
    "Toronto Raptors": {"abbreviation": "TOR", "from": "1995-01-01", "to": None},
    "Utah Jazz": {"abbreviation": "UTA", "from": "1979-01-01", "to": None},
    "Vancover Grizzlies": {
        "abbreviation": "VAN",
        "from": "1995-01-01",
        "to": "2001-01-01",
    },
    "Washington Wizards": {"abbreviation": "WAS", "from": "1997-01-01", "to": None},
    "Washington Bullets": {
        "abbreviation": "WSB",
        "from": "1969-01-01",
        "to": "1997-01-01",
    },
}


def load_teams_data() -> List[Dict[str, Any]]:
    """
    Load teams data from database or backup file.

    Returns:
        List of team dictionaries
    """
    # Try to load from database first
    try:
        conn = get_connection()
        teams_df = pl.read_database(query="SELECT * FROM teams", connection=conn)
        conn.close()

        if not teams_df.is_empty():
            return teams_df.rows(named=True)
    except Exception:
        pass

    # Fall back to file
    teams_file = Path(__file__).parent.parent.parent / "data" / "teams.json"
    if teams_file.exists():
        with open(teams_file, "r") as f:
            return json.load(f)

    # Fall back to hardcoded abbreviations if all else fails
    return [
        {"name": name, "abbreviation": info["abbreviation"]}
        for name, info in TEAM_ABBREVIATION_HISTORY.items()
    ]


def get_team_abbreviation(team_name: str, date: Optional[date] = None) -> str:
    """
    Get team abbreviation for a team name, considering historical changes.

    Args:
        team_name: Team name
        date: Date for which to get the abbreviation

    Returns:
        Team abbreviation
    """
    if not team_name:
        return ""

    # Convert date to datetime if needed
    if date and not isinstance(date, datetime):
        date = datetime.combine(date, datetime.min.time())

    # Check if team name is already an abbreviation (3 letters)
    if len(team_name) == 3 and team_name.isupper():
        return team_name

    # Look up in history
    for name, info in TEAM_ABBREVIATION_HISTORY.items():
        if team_name.upper() == name.upper():
            from_date = datetime.strptime(info["from"], "%Y-%m-%d")
            to_date = datetime.strptime(info["to"], "%Y-%m-%d") if info["to"] else None

            if date:
                if from_date <= date and (not to_date or date < to_date):
                    return info["abbreviation"]
            else:
                # If no date specified, return most recent abbreviation
                if not to_date:
                    return info["abbreviation"]

    # Try to find by partial match
    team_name_upper = team_name.upper()
    for name, info in TEAM_ABBREVIATION_HISTORY.items():
        if team_name_upper in name.upper():
            return info["abbreviation"]

    # If all else fails, return first 3 chars
    return team_name[:3].upper()


def get_abbreviation(teams: List[Dict[str, Any]], team_name: str) -> str:
    """
    Get team abbreviation from a list of team dictionaries.

    Args:
        teams: List of team dictionaries
        team_name: Team name to look up

    Returns:
        Team abbreviation
    """
    if not team_name:
        return ""

    # Check if team_name is already an abbreviation
    if len(team_name) == 3 and team_name.isupper():
        return team_name

    # Search in teams list
    for team in teams:
        if team["name"].upper() == team_name.upper():
            return team["abbreviation"]

    # Fall back to the general function
    return get_team_abbreviation(team_name)


def get_team_logo_url(team_abbreviation: str) -> str:
    """
    Get the URL for the team's logo based on its abbreviation.

    Args:
        team_abbreviation: Team abbreviation

    Returns:
        URL for the team's logo
    """
    return f"https://raw.githubusercontent.com/HTilki/NBAStatsApp/bff918fd85d639dcb23449669f26c0b536a43635/images/teams_logos/{team_abbreviation}.svg"
