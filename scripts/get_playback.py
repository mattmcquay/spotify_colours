#!/usr/bin/env python3
"""Fetch current playback from Spotify and print the artwork URL.

Usage:
    python scripts/get_playback.py [--download OUTPUT_PATH]

If no token is cached, run `scripts/auth_local.py` first to authenticate.
"""
import sys
import os
import argparse
import json
from typing import List
from urllib.parse import urlparse

# ensure repo root on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.auth import get_oauth_manager, load_cached_token
from src.spotify_client import SpotifyClient


def download_url(url: str, out_path: str) -> None:
    try:
        import requests
    except Exception:
        raise RuntimeError("`requests` is required to download images. Install with `pip install requests`.")
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    with open(out_path, "wb") as fh:
        fh.write(r.content)


def main(argv: List[str]) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--download", "-d", help="Optional path to save artwork image")
    args = p.parse_args(argv)

    # Prefer cached token if present (so get_oauth_manager won't force a browser flow)
    cached = load_cached_token()
    if cached:
        mgr = get_oauth_manager(None, None, scope="user-read-playback-state,user-read-currently-playing")
    else:
        print("No cached token found. Run `python scripts/auth_local.py` to authenticate first.")
        return 2

    client = SpotifyClient(auth_manager=mgr)
    playback = client.current_playback()
    if not playback:
        print("No current playback found (None). Make sure a device is active and something is playing.")
        return 0

    artwork = client.get_artwork_url(playback)
    print(json.dumps(playback, indent=2))
    print("\nArtwork URL:", artwork)

    if args.download and artwork:
        out_path = args.download
        print(f"Downloading artwork to {out_path}...")
        try:
            download_url(artwork, out_path)
            print("Downloaded OK")
        except Exception as exc:
            print("Download failed:", exc)
            return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
