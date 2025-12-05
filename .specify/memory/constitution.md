# Spotify Colours — Constitution

## Core Principles

### I. Minimal, Library-First
Every capability (auth, Spotify client, colour extraction, pattern generator, output drivers) should be designed as a small, testable library with a clear single responsibility.

### II. Dual Interface (API + CLI)
All core features must be accessible programmatically (library API) and via a simple CLI for manual testing and debugging.

### III. Test-First & Deterministic
Unit tests and deterministic behaviour are required for colour extraction and pattern generation to avoid surprises in downstream outputs.

### IV. Security-First
Secrets (client secret, refresh tokens) must never be committed; prefer environment variables or OS-backed secret stores. Logging must avoid sensitive data.

### V. Observability & Simplicity
Prefer simple, auditable behaviour over premature optimization. Provide structured logs and small, understandable failure modes.

## Additional Constraints

- Supported runtimes: Python (acceptable). Keep the implementation small and dependency-light.
- Use Spotify Web API (Authorization Code with refresh) for user playback data.
- Respect rate limits and backoff on transient API errors.

## Development Workflow

- Follow a test-first approach for new features related to colour extraction, pattern generation, and the Spotify wrapper.
- Use short-lived feature branches and PRs. Include unit tests and maintainers must approve breaking changes.
- CI should run unit tests and basic linting; integration tests that require Spotify credentials should be gated and/or mocked.

## Governance

Constitution amendments require a PR that documents the change rationale, a migration plan (if applicable), and tests demonstrating compatibility. The maintainers team reviews and ratifies changes.

**Version**: 0.1 | **Ratified**: 2025-12-05 | **Last Amended**: 2025-12-05

## Purpose (project-specific summary)
Provide minimal, concrete requirements for a small project which:
- connects to Spotify for a configurable user's "currently playing" information;
- obtains the current track's album artwork;
- extracts the top 4 colours from that artwork into an ordered array (hex strings);
- exposes a repeatable pattern generator that turns that array into a colour sequence consumable by pluggable output drivers.

## Scope
- Implement Spotify integration for the authenticated user (OAuth flow and token refresh).
- Download and analyse album artwork for the currently playing track.
- Extract and return the top 4 dominant colours as an array of hex strings (ordered by dominance).
- Provide a pattern generator and an abstract `OutputDriver` interface; concrete drivers are implemented later.

## Functional Requirements
1. Support fetching the "currently playing" or "currently playing" state for the authenticated user.
2. When a new track is detected (or artwork changes), download the album artwork.
3. Extract the top 4 dominant colours and return them as hex strings (e.g., `#AABBCC`).
4. Provide a pattern generator that maps the 4-colour array into a repeatable sequence.
5. Expose a minimal programmatic API and a CLI run mode for manual operation.

## Non-functional Requirements
- Colour extraction should be efficient (image downscale + quantization) and deterministic.
- Default polling interval: 5s; configurable via environment or config file.
- Secrets must be stored outside of the repository; avoid logging tokens.

## Spotify Authorization
- Use OAuth Authorization Code flow with refresh tokens.
- Minimal scopes: `user-read-playback-state`, `user-read-currently-playing`.
- Store `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`, and refresh tokens in environment variables or a local config excluded from VCS.

## Example Configuration Keys
```
SPOTIFY_CLIENT_ID=
SPOTIFY_CLIENT_SECRET=
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
POLL_INTERVAL_SECONDS=5
PATTERN_MODE=repeat
PATTERN_LENGTH=32
```

## Data Flow (high level)
1. User authorizes app via OAuth → obtain access + refresh tokens.
2. Poll Spotify's currently playing endpoint at configured interval.
3. If the track/artwork changed, fetch artwork bytes and compute top-4 colours.
4. Generate a pattern from the 4 colours.
5. Provide the pattern to an `OutputDriver` for delivery.

## Colour Extraction Requirements
- Input: image bytes or image URL (JPEG/PNG).
- Output: ordered array of 4 hex colour strings.
- Algorithm constraints: downscale image (e.g., 200px max), quantize (k-means or median cut), sort by pixel count, return top 4.
- Suggested libraries: Python: `colorthief`, `spotipy`, `requests`.

## Pattern Generator (API)
- Accepts `colors: list[]` and `opts` (mode, length, step).
- Returns `list[]` sequence of hex colours.
- Modes: `repeat`, `mirror`, `rotate` (simple deterministic behaviours).

## OutputDriver (abstract interface)
- `connect(): `
- `send(colors: string[]): `
- `close(): `

## Testing
- Unit tests for colour extraction with image fixtures verifying deterministic top-4 output.
- Unit tests for pattern generator modes and lengths.
- Integration tests should mock Spotify responses; real Spotify tests can be run manually with credentials.

## Security & Privacy
- Do not log raw image bytes or tokens.
- Mark config files with secrets as ignored by VCS.

## Minimal File Layout
```
src/
	auth/
	spotify/
	colours/
	outputs/
cli.py
tests/
config/
```