"""Colour extraction and pattern generator.

This module previously contained a deterministic stub. It now supports
downloading an artwork image into a cache directory, extracting the top-4
colours using Pillow, and removing the downloaded image afterwards. For
non-URL inputs the previous deterministic stub behaviour is preserved.
"""
import hashlib
import os
import shutil
from pathlib import Path
from typing import List, Optional, Tuple

import requests
from PIL import Image


def _digest_to_rgb(d: bytes) -> str:
    r, g, b = d[0], d[1], d[2]
    return f"#{r:02X}{g:02X}{b:02X}"


def _ensure_cache_dir(cache_dir: Optional[str]) -> Path:
    if cache_dir:
        p = Path(cache_dir)
    else:
        # Default cache path inside project: ./cache/images
        repo_root = Path(__file__).resolve().parents[1]
        p = repo_root / "cache" / "images"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _download_image(url: str, cache_dir: Path) -> Path:
    # Use an md5 of the url for a filename; keep extension if present
    h = hashlib.md5(url.encode("utf-8")).hexdigest()
    ext = Path(url).suffix
    if not ext or len(ext) > 6:
        ext = ".jpg"
    out = cache_dir / f"{h}{ext}"
    # Stream download to file
    resp = requests.get(url, stream=True, timeout=15)
    resp.raise_for_status()
    with open(out, "wb") as fh:
        for chunk in resp.iter_content(1024 * 8):
            if chunk:
                fh.write(chunk)
    return out


def _extract_top4_from_file(path: Path) -> List[str]:
    # Open image, quantize to a small palette, and return top 4 non-white colours
    with Image.open(path) as img:
        img = img.convert("RGBA")
        # Composite against white to remove transparency
        if img.mode == "RGBA":
            background = Image.new("RGBA", img.size, (255, 255, 255, 255))
            img = Image.alpha_composite(background, img).convert("RGB")
        else:
            img = img.convert("RGB")

        # Resize to speed up processing
        max_size = (200, 200)
        img.thumbnail(max_size, Image.LANCZOS)

        # Quantize to a small palette
        pal = img.convert("P", palette=Image.ADAPTIVE, colors=8)
        palette = pal.getpalette() or []
        color_counts = pal.getcolors(pal.size[0] * pal.size[1]) or []

        # Map palette index to RGB and count
        counted: List[Tuple[int, Tuple[int, int, int]]] = []
        for count, idx in color_counts:
            i = idx * 3
            r = palette[i]
            g = palette[i + 1]
            b = palette[i + 2]
            counted.append((count, (r, g, b)))

        # Sort by frequency desc
        counted.sort(reverse=True, key=lambda x: x[0])

        colours: List[str] = []
        for _, (r, g, b) in counted:
            # Skip near-white colours
            if r >= 245 and g >= 245 and b >= 245:
                continue
            hexc = f"#{r:02X}{g:02X}{b:02X}"
            if hexc not in colours:
                colours.append(hexc)
            if len(colours) >= 4:
                break

        # If we didn't find enough colours, fall back to deterministic stub
        if len(colours) < 4:
            fallback = extract_top4_from_digest(path.read_bytes())
            for c in fallback:
                if c not in colours:
                    colours.append(c)
                if len(colours) >= 4:
                    break

        return colours[:4]


def extract_top4_from_digest(content: bytes) -> List[str]:
    # Helper fallback that uses md5 of bytes to produce deterministic colours
    h = hashlib.md5(content).digest()
    colours = []
    for i in range(4):
        start = (i * 3) % len(h)
        group = h[start:start + 3]
        if len(group) < 3:
            group = (group + h)[:3]
        colours.append(_digest_to_rgb(group))
    return colours


def extract_top4(source_identifier: str, cache_dir: Optional[str] = None) -> List[str]:
    """Extract top-4 hex colours.

    - If `source_identifier` looks like an HTTP URL it will be downloaded into
      a cache directory, processed, and the downloaded file removed.
    - If `source_identifier` is not a URL the previous deterministic stub
      behaviour is preserved (hash-based colours).

    Returns a list of four hex colour strings (e.g. `#A1B2C3`).
    """
    if not source_identifier:
        source_identifier = ""

    is_url = source_identifier.startswith("http://") or source_identifier.startswith("https://")
    if not is_url:
        # Preserve old stub behaviour for non-URL inputs
        h = hashlib.md5(source_identifier.encode("utf-8")).digest()
        colours = []
        for i in range(4):
            start = (i * 3) % len(h)
            group = h[start:start + 3]
            if len(group) < 3:
                group = (group + h)[:3]
            colours.append(_digest_to_rgb(group))
        return colours

    # Otherwise, download and process the image
    cache_path = _ensure_cache_dir(cache_dir)
    downloaded: Optional[Path] = None
    try:
        downloaded = _download_image(source_identifier, cache_path)
        colours = _extract_top4_from_file(downloaded)
        return colours
    finally:
        # Remove the downloaded original file (cleanup)
        try:
            if downloaded and downloaded.exists():
                downloaded.unlink()
        except Exception:
            # Don't let cleanup errors crash the caller
            pass


def generate_pattern(colors: List[str], length: int = 16, mode: str = "repeat") -> List[str]:
    """Generate a repeatable colour sequence from four colours.

    Modes:
    - repeat: ABCDABCD...
    - mirror: ABCDDCBAABCD...
    - rotate: rotate the base array each cycle
    """
    if not colors or len(colors) < 4:
        raise ValueError("colors must be a list of 4 hex strings")
    base = colors[:4]
    seq: List[str] = []
    if mode == "repeat":
        while len(seq) < length:
            for c in base:
                if len(seq) >= length:
                    break
                seq.append(c)
    elif mode == "mirror":
        mirror = base + base[::-1]
        while len(seq) < length:
            for c in mirror:
                if len(seq) >= length:
                    break
                seq.append(c)
    elif mode == "rotate":
        i = 0
        while len(seq) < length:
            seq.append(base[i % 4])
            i += 1
    else:
        raise ValueError(f"unknown mode: {mode}")
    return seq
