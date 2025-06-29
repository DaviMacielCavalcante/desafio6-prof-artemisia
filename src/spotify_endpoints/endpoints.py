import requests as r
import os
import pprint

def get_recently_played() -> None:
    headers = {
        "Authorization": f"Bearer {os.getenv('ACCESS_TOKEN')}"
    }

    response = r.get("https://api.spotify.com/v1/me/player/recently-played", headers=headers)

    pprint.pprint(response.json().get("items"))