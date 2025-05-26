"""
Team Utilities Module
Centralized functions for handling team names, abbreviations, and team-related operations.
"""

from typing import Optional, Dict, List, Any
from datetime import datetime


# Team abbreviation history for different eras
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
    "Vancouver Grizzlies": {
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


def get_team_abbreviation(teams: List[Dict[str, Any]], team_name: str) -> str:
    """
    Get team abbreviation from team name using the teams list.

    Args:
        teams: List of team dictionaries from database
        team_name: Team name to look up

    Returns:
        Team abbreviation or empty string if not found
    """
    for team in teams:
        if team["name"].lower() == team_name.lower():
            return team["abbreviation"]
    return ""


def get_team_name_by_abbreviation(
    teams: List[Dict[str, Any]], abbreviation: str
) -> str:
    """
    Get team name from team abbreviation.

    Args:
        teams: List of team dictionaries from database
        abbreviation: Team abbreviation to look up

    Returns:
        Team name or the abbreviation if not found
    """
    # Check if abbreviation is already a full team name
    if len(abbreviation) > 3:
        return abbreviation

    # Look up in teams list
    for team in teams:
        if team["abbreviation"].upper() == abbreviation.upper():
            return team["name"]

    # If not found, return the abbreviation
    return abbreviation


def format_team_name(name: str) -> str:
    """
    Format a team name for display.

    Args:
        name: Team name

    Returns:
        Formatted team name
    """
    if not name:
        return ""
    return name.upper()


def get_team_logo_url(team_abbreviation: str) -> str:
    """
    Get the logo URL for a team given their abbreviation.

    Args:
        team_abbreviation: The team's abbreviation

    Returns:
        The path to the team's logo file
    """
    return f"images/teams_logos/{team_abbreviation}.svg"


def get_historical_abbreviation(
    team_name: str, date_context: Optional[datetime] = None
) -> str:
    """
    Get historical team abbreviation based on team name and date context.

    Args:
        team_name: Team name
        date_context: Date to determine the correct abbreviation for that era

    Returns:
        Team abbreviation for the given time period
    """
    if date_context is None:
        date_context = datetime.now()

    team_info = TEAM_ABBREVIATION_HISTORY.get(team_name)
    if not team_info:
        return ""

    from_date = datetime.fromisoformat(team_info["from"])
    to_date = (
        datetime.fromisoformat(team_info["to"]) if team_info["to"] else datetime.now()
    )

    if from_date <= date_context <= to_date:
        return team_info["abbreviation"]

    return ""
