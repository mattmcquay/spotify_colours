#!/usr/bin/env python3
"""Continuously poll Spotify playback and print the current album artwork URL.

The script reads Spotify credentials from environment variables (or a local
.env loaded by other tooling) and uses spotipy's `SpotifyOAuth` caching
mechanism (the default cache file is `.cache-spotify`). It will exit when
the cached token indicates it has expired.

Arguments:
  --interval N     Poll interval in seconds (default: 60)
  --max-loops N    Run at most N loops then exit (useful for testing)
"""
import argparse
import sys
import time
from pathlib import Path
from typing import Optional, List
import json

# Make sure project root is importable when running from scripts/
repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.auth import get_oauth_manager
import spotipy
from src import colours


# Rotation state: when the same artwork repeats, rotate the base colours
# so the emitted pattern appears to animate.
class _RotationState:
    def __init__(self):
        self.prev_art: Optional[str] = None
        self.rotation: int = 0
        self.base: List[str] = []


def run_loop(interval: int = 60, max_loops: Optional[int] = None) -> int:
    manager = get_oauth_manager()

    token_info = manager.get_cached_token()
    if not token_info:
        print("No cached token found. Run scripts/auth_local.py to authenticate.")
        return 2

    expires_at = token_info.get("expires_at", 0)
    loops = 0

    state = _RotationState()

    while True:
        now = int(time.time())
        if expires_at and now >= expires_at:
            print(f"Token expired at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expires_at))}. Exiting.")
            return 0

        sp = spotipy.Spotify(auth_manager=manager)
        try:
            playback = sp.current_playback()
        except Exception as exc:  # pragma: no cover - network/runtime behaviour
            print("Error fetching playback:", exc)
            return 1

        art = None
        try:
            if playback and playback.get("item") and playback["item"].get("album"):
                images = playback["item"]["album"].get("images") or []
                if images:
                    art = images[0].get("url")
        except Exception:
            art = None

        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # Compute colours and pattern
        pattern_str = None
        pattern = None
        base = []
        try:
            if art:
                if art != state.prev_art:
                    # New artwork: extract colours and reset rotation
                    state.base = colours.extract_top4(art)
                    state.rotation = 0
                    state.prev_art = art
                else:
                    # Same artwork as previous loop: increment rotation
                    state.rotation = (state.rotation + 1) % 4

                # Rotate base colours by state.rotation and generate pattern
                base = state.base[state.rotation:] + state.base[:state.rotation]
                pattern = colours.generate_pattern(base, length=16, mode="repeat")
                pattern_str = ",".join(pattern)

        except Exception as exc:  # pragma: no cover - runtime/image errors
            pattern_str = f"(error extracting colours: {exc})"

        print(f"[{ts}] Artwork: {art} | Pattern: {pattern_str}")

        # Also write the current palette/pattern to cache/current_palette.json
        try:
            cache_dir = repo_root / "cache"
            cache_dir.mkdir(parents=True, exist_ok=True)
            out = cache_dir / "current_palette.json"
            payload = {
                "timestamp": ts,
                "artwork": art,
                "base": base,
                "rotation": state.rotation,
                "pattern": pattern,
            }
            with open(out, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, ensure_ascii=False)
        except Exception:
            # Don't let write errors break polling
            pass

        # Refresh token info from cache (spotipy updates cache when refreshing)
        token_info = manager.get_cached_token()
        if token_info:
            expires_at = token_info.get("expires_at", expires_at)

        loops += 1
        if max_loops and loops >= max_loops:
            return 0

        time.sleep(interval)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--interval", type=int, default=60, help="poll interval seconds")
    p.add_argument("--max-loops", type=int, default=None, help="run N loops then exit (testing)")
    return p.parse_args()


def main():
    args = parse_args()
    return run_loop(interval=args.interval, max_loops=args.max_loops)


if __name__ == "__main__":
    sys.exit(main())
