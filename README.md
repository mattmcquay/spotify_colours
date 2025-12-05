# spotify_colours (scaffold)

Minimal scaffold for the Spotify Colours project. This project will:
- connect to Spotify for the authenticated user's currently-playing information;
- fetch album artwork and extract the top-4 colours as hex strings;
- generate repeatable colour patterns and pass them to output drivers.

This scaffold includes a deterministic colour-extraction stub, a pattern generator, a small `ConsoleOutputDriver`, a simple CLI, and unit tests for the pattern generator.

Quick start (python):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt  # optional
python cli.py demo
python -m unittest discover -v
```
