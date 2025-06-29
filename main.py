from src.auth.spotify_auth import auth_flow
from src.spotify_endpoints.endpoints import get_recently_played

auth_flow()

get_recently_played()