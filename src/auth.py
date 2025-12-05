"""OAuth helpers for spotify_colours.

This module provides a small interactive flow to obtain an OAuth token
for a user using Spotify's Authorization Code flow. It loads credentials
from environment variables or a local `.env` file and uses spotipy's
`SpotifyOAuth` for token handling.

The interactive flow opens a browser and asks you to paste the redirect
URL back into the console. Tokens are cached to `.cache-spotify` by
default (spotipy cache). Do not commit cache or `.env` files containing
secrets.
"""

import os
import webbrowser
from typing import Dict, Optional

from spotipy.oauth2 import SpotifyOAuth


DEFAULT_CACHE = ".cache-spotify"


def _load_dotenv(path: str = ".env") -> None:
    """Load a simple KEY=VALUE .env file into `os.environ` when keys are not set.

    Lines beginning with `#` and empty lines are ignored. Existing
    environment variables are not overwritten.
    """
    if not os.path.exists(path):
        return
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip()
                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                if key and key not in os.environ:
                    os.environ[key] = val
    except Exception:
        return


_load_dotenv()


def get_oauth_manager(
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    redirect_uri: Optional[str] = None,
    scope: str = "user-read-playback-state",
    cache_path: str = DEFAULT_CACHE,
) -> SpotifyOAuth:
    """Return a configured `SpotifyOAuth` instance.

    Credentials are resolved from provided args first, then environment
    variables (`SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`, `SPOTIFY_REDIRECT_URI`).
    """
    client_id = client_id or os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = client_secret or os.getenv("SPOTIFY_CLIENT_SECRET")
    redirect_uri = redirect_uri or os.getenv("SPOTIFY_REDIRECT_URI") or "http://localhost:8080"

    if not client_id or not client_secret:
        raise RuntimeError("Spotify client_id and client_secret must be provided via args or environment variables")

    return SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scope,
        cache_path=cache_path,
    )


def interactive_authorize(
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    redirect_uri: Optional[str] = None,
    scope: str = "user-read-playback-state",
    cache_path: str = DEFAULT_CACHE,
) -> Dict[str, str]:
    """Run interactive authorization and return token_info.

    Opens the authorization URL and prompts you to paste the full redirect
    URL back into the console. Returns spotipy's `token_info` dict.
    """
    oauth = get_oauth_manager(client_id, client_secret, redirect_uri, scope, cache_path)
    auth_url = oauth.get_authorize_url()

    print("Opening your browser to complete Spotify login...")
    webbrowser.open(auth_url)
    print("If your browser does not open, visit this URL and authenticate:")
    print(auth_url)
    redirected = input("After authorizing, paste the full redirect URL here: ").strip()

    code = oauth.parse_response_code(redirected)
    token_info = oauth.get_access_token(code)
    return token_info


def load_cached_token(cache_path: str = DEFAULT_CACHE) -> Optional[Dict[str, str]]:
    """Load token_info from spotipy cache, or return None.

    Use the configured `get_oauth_manager` so credentials are resolved
    from the project's environment/config loader rather than relying on
    spotipy-specific env vars (e.g. `SPOTIPY_CLIENT_ID`).
    """
    try:
        oauth = get_oauth_manager(None, None, cache_path=cache_path)
        token_info = oauth.get_cached_token()
    except Exception:
        token_info = None
    return token_info
