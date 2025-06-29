import requests as r
from dotenv import load_dotenv, set_key
import os
import uuid
import pprint
import webbrowser
from urllib.parse import urlparse, parse_qs
import base64
def get_authorization_code(client_id: str, redirect_uri: str, state: str) -> None:

    load_dotenv(override=True)

    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": "user-read-private user-read-email user-read-recently-played", 
        "state": state
    }

    response = r.get("https://accounts.spotify.com/authorize", params=params)

    webbrowser.open(response.url)
    callback_url = input("Digite a URL de callback: ")
    parsed_url = urlparse(callback_url)
    query_params = parse_qs(parsed_url.query)

    authorization_code = query_params.get("code")
    pprint.pprint(f"Authorization Code: {authorization_code[0] if authorization_code else 'Not found'}")
    set_key(".env", "AUTHORIZATION_CODE", authorization_code[0])

def get_access_token(redirect_uri: str, code: str, authorization_code: str) -> None:
    load_dotenv(override=True)
    body = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": authorization_code
    }

    response = r.post("https://accounts.spotify.com/api/token", data=body, headers=headers)
    pprint.pprint(response.json())
    access_token = response.json().get("access_token")
    refresh_token = response.json().get("refresh_token")
    set_key(".env", "ACCESS_TOKEN", access_token)
    set_key(".env", "REFRESH_TOKEN", refresh_token)


def refresh_token(refresh_token: str, authorization_code: str) -> None:
    load_dotenv(override=True)
    body = {
        "grant_type": "refresh_token",
        "refresh_token": os.getenv("REFRESH_TOKEN")
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": authorization_code
    }

    response = r.post("https://accounts.spotify.com/api/token", data=body, headers=headers)
    if response.json().get("refresh_token"):
        pprint.pprint(response.json())
        set_key(".env", "REFRESH_TOKEN", response.json().get("refresh_token"))
    else:
        set_key(".env", "ACCESS_TOKEN", response.json().get("access_token"))

def auth_flow() -> None:
    set_key(".env", "AUTHORIZATION_CODE", "")
    get_authorization_code(os.getenv("CLIENT_ID"), os.getenv("REDIRECT_URI"), str(uuid.uuid4()))
    load_dotenv(override=True)
    get_access_token(os.getenv("REDIRECT_URI"), os.getenv("AUTHORIZATION_CODE"), f"Basic {base64.b64encode(f'{os.getenv('CLIENT_ID')}:{os.getenv('CLIENT_SECRET')}'.encode()).decode()}")
    refresh_token(os.getenv("REFRESH_TOKEN"), f"Basic {base64.b64encode(f'{os.getenv('CLIENT_ID')}:{os.getenv('CLIENT_SECRET')}'.encode()).decode()}")