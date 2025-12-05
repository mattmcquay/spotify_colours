"""Spotify client wrapper.

This module provides `SpotifyClient`, a thin wrapper around `spotipy.Spotify`.
It accepts an auth manager or raw token info and exposes helpers used by the
rest of the project (e.g., `current_playback` and `get_artwork_url`).
"""
from typing import Any, Dict, Optional

import spotipy


class SpotifyClient:
    def __init__(self, auth_manager: Optional[Any] = None, access_token: Optional[str] = None):
        """Create SpotifyClient.

        Provide either an `auth_manager` (e.g., `SpotifyOAuth`) or an
        `access_token`. When `auth_manager` is provided we construct a
        `spotipy.Spotify(auth_manager=...)` instance which will handle
        token refreshes automatically.
        """
        if spotipy is None:
            raise RuntimeError("spotipy is required. Install with `pip install spotipy`.")
        if auth_manager is not None:
            self._sp = spotipy.Spotify(auth_manager=auth_manager)
        elif access_token is not None:
            self._sp = spotipy.Spotify(auth=access_token)
        else:
            raise ValueError("Either auth_manager or access_token must be provided")

    def current_playback(self) -> Dict[str, Any]:
        """Return the currently-playing object from Spotify API."""
        return self._sp.current_playback()

    @staticmethod
    def get_artwork_url(playback_obj: Dict[str, Any]) -> Optional[str]:
        """Extract the first artwork URL from a playback object, if present."""
        if not playback_obj:
            return None
        item = playback_obj.get("item")
        if not item:
            return None
        album = item.get("album") or {}
        images = album.get("images") or []
        if not images:
            return None
        # Spotify returns images sorted largest -> smallest; pick the first
        return images[0].get("url")

    def refresh_token(self) -> None:
        """Force a token refresh if using an auth_manager with refresh support.

        This delegates to the auth manager (spotipy handles it internally on API calls,
        but exposing an explicit hook can be useful).
        """
        # spotipy's auth_manager will refresh tokens automatically when needed.
        # No-op provided for API completeness.
        return

