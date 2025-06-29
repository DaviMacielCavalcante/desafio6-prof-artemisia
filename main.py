import requests as r
from requests_oauthlib import OAuth2Session
import json
from dotenv import load_dotenv, set_key
import os
import uuid
import pprint
import webbrowser
from urllib.parse import urlparse, parse_qs
import base64

def get_authorization_code():

    load_dotenv()

    client_id = os.getenv("CLIENT_ID")
    redirect_uri = os.getenv("REDIRECT_URI")

    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": "user-read-private user-read-email user-read-recently-played", 
        "state": str(uuid.uuid4())
    }
    response = r.get("https://accounts.spotify.com/authorize", params=params)
    webbrowser.open(response.url)
    callback_url = input("Digite a URL de callback: ")
    parsed_url = urlparse(callback_url)
    query_params = parse_qs(parsed_url.query)

    authorization_code = query_params.get("code")
    set_key(".env", "AUTHORIZATION_CODE", authorization_code[0])

def get_access_token():
    load_dotenv()
    client_secret = os.getenv("CLIENT_SECRET")
    client_id = os.getenv("CLIENT_ID")
    body = {
        "grant_type": "authorization_code",
        "code": os.getenv("AUTHORIZATION_CODE"),
        "redirect_uri": os.getenv("REDIRECT_URI")
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {base64.b64encode(f'{client_id}:{client_secret}'.encode()).decode()}"
    }
    response = r.post("https://accounts.spotify.com/api/token", data=body, headers=headers)
    pprint.pprint(response.json())
    access_token = response.json().get("access_token")
    refresh_token = response.json().get("refresh_token")
    set_key(".env", "ACCESS_TOKEN", access_token)
    set_key(".env", "REFRESH_TOKEN", refresh_token)


def refresh_token():
    load_dotenv()
    body = {
        "grant_type": "refresh_token",
        "refresh_token": os.getenv("REFRESH_TOKEN")
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {base64.b64encode(f'{os.getenv("CLIENT_ID")}:{os.getenv("CLIENT_SECRET")}'.encode()).decode()}"
    }

    response = r.post("https://accounts.spotify.com/api/token", data=body, headers=headers)
    if response.json().get("refresh_token"):
        pprint.pprint(response.json())
        set_key(".env", "REFRESH_TOKEN", response.json().get("refresh_token"))


get_authorization_code()
get_access_token()
refresh_token()