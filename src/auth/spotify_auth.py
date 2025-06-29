import requests as r
from dotenv import load_dotenv, set_key
import os
import uuid
import pprint
import webbrowser
from urllib.parse import urlparse, parse_qs
import base64

def get_authorization_code(client_id: str, redirect_uri: str, state: str) -> None:

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

def get_access_token(redirect_uri: str, authorization_code: str, encoded_credentials: str) -> None:
    body = {
        "grant_type": "authorization_code",
        "code": authorization_code,
        "redirect_uri": redirect_uri
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": encoded_credentials
    }

    response = r.post("https://accounts.spotify.com/api/token", data=body, headers=headers)
    pprint.pprint(response.json())
    access_token = response.json().get("access_token")
    refresh_token = response.json().get("refresh_token")
    set_key(".env", "ACCESS_TOKEN", access_token)
    set_key(".env", "REFRESH_TOKEN", refresh_token)


def refresh_token(refresh_token: str, encoded_credentials: str) -> None:
    body = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": encoded_credentials
    }

    response = r.post("https://accounts.spotify.com/api/token", data=body, headers=headers)
    if response.json().get("refresh_token"):
        pprint.pprint(response.json())
        set_key(".env", "REFRESH_TOKEN", response.json().get("refresh_token"))
    else:
        set_key(".env", "ACCESS_TOKEN", response.json().get("access_token"))

def uuid_generator() -> str:
    return str(uuid.uuid4())

def encode_client_credentials(client_id: str, client_secret: str) -> str:
    credentials = f"{client_id}:{client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded_credentials}"

def auth_flow() -> None:
    set_key(".env", "AUTHORIZATION_CODE", "")

    load_dotenv(override=True)

    client_id = os.getenv("CLIENT_ID")
    redirect_uri = os.getenv("REDIRECT_URI")
    client_secret = os.getenv("CLIENT_SECRET")
    encoded_client_credentials = encode_client_credentials(client_id, client_secret)
    random_state = uuid_generator()

    get_authorization_code(client_id,redirect_uri, random_state)

    load_dotenv(override=True)

    authorization_code = os.getenv("AUTHORIZATION_CODE")

    get_access_token(redirect_uri, authorization_code, encoded_client_credentials)

    load_dotenv(override=True)

    refresh_token_value = os.getenv("REFRESH_TOKEN")

    refresh_token(refresh_token_value, encoded_client_credentials)