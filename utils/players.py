def get_player_photo_url(player_id: str) -> str:
    """
    Get the photo URL for a player given their ID.

    Args:
        player_id (str): The player's ID.

    Returns:
        str: The URL of the player's photo.
    """
    return f"https://cdn.nba.com/headshots/nba/latest/260x190/{player_id}.png"
