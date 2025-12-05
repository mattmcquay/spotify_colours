#!/usr/bin/env python3
"""Run Spotify Authorization Code flow with an automatic local callback.

This script reads `SPOTIFY_REDIRECT_URI` and credentials from environment
or `.env` (the project's loader), constructs the authorize URL, opens the
browser, listens for a single HTTP request to capture the `code` query
parameter and exchanges it for `token_info` using spotipy's
`SpotifyOAuth`.

Usage:
    python scripts/auth_local.py

The redirect host/port/path must be registered in your Spotify App
Redirect URIs (developer dashboard) and must match `SPOTIFY_REDIRECT_URI`.
"""
import json
import sys
import os
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Tuple

# Ensure repo root is on sys.path so `src` can be imported when running
# the script from the `scripts/` directory.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.auth import get_oauth_manager


class _CallbackHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:  # quiet logging
        return

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        code = params.get("code", [None])[0]
        error = params.get("error", [None])[0]
        # store on server so caller can read
        self.server.auth_code = code
        self.server.auth_error = error

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        if code:
            self.wfile.write(b"<html><body><h1>Authorization complete</h1><p>You can close this window.</p></body></html>")
        else:
            self.wfile.write(b"<html><body><h1>Authorization failed</h1><p>Check the terminal for details.</p></body></html>")


def _parse_redirect(uri: str) -> Tuple[str, int, str]:
    p = urlparse(uri)
    host = p.hostname or "127.0.0.1"
    port = p.port or 80
    path = p.path or "/"
    return host, port, path


def main() -> int:
    scope = "user-read-playback-state user-read-currently-playing"
    # get an oauth manager that uses the project's env/config loader
    oauth = get_oauth_manager(None, None, scope=scope)
    auth_url = oauth.get_authorize_url()

    redirect_uri = oauth.redirect_uri
    host, port, path = _parse_redirect(redirect_uri)

    print(f"Opening browser for authorization (redirect -> {redirect_uri})...")
    webbrowser.open(auth_url)

    server_address = (host, port)
    httpd = HTTPServer(server_address, _CallbackHandler)
    # handle a single request (the redirect) then continue
    try:
        httpd.handle_request()
    except KeyboardInterrupt:
        print("Interrupted, exiting")
        return 1

    code = getattr(httpd, "auth_code", None)
    error = getattr(httpd, "auth_error", None)
    if error:
        print("Authorization error:", error)
        return 2
    if not code:
        print("No authorization code received")
        return 3

    # Exchange code for tokens (spotipy will also cache to the configured cache_path)
    token_info = oauth.get_access_token(code)
    print(json.dumps(token_info, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
