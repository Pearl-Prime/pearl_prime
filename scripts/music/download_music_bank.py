#!/usr/bin/env python3
"""Download free music tracks from Pixabay and FreePD for the video music bank.

Usage:
    python3 scripts/music/download_music_bank.py --max-tracks 50
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print("requests required: pip install requests", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
OUT = REPO_ROOT / "assets" / "music_bank"


def download_pixabay(max_tracks: int = 50) -> list[dict]:
    """Download ambient/calm tracks from Pixabay Music."""
    # Pixabay API key (free, just register)
    api_key = os.environ.get("PIXABAY_API_KEY", "")
    
    # Pixabay doesn't have a public music API with direct download,
    # but we can search their music page and download manually.
    # For automation, we'll use their web search endpoint.
    
    # Alternative: direct download known good ambient tracks from FreePD
    print("Pixabay requires manual download or API key.", flush=True)
    print("Falling back to FreePD (fully automated, CC0)...", flush=True)
    return []


def download_freepd(max_tracks: int = 50) -> list[dict]:
    """Download CC0 tracks from FreePD."""
    categories = {
        "calm": "https://freepd.com/music/Calm%20and%20Peaceful.mp3",
        "ambient": "https://freepd.com/music/Ambient.mp3",
    }
    
    # FreePD has direct download links but they're individual tracks
    # Let's download from their categories
    base = "https://freepd.com"
    
    downloaded = []
    print(f"FreePD: downloading up to {max_tracks} tracks...", flush=True)
    
    # Known good ambient/calm tracks from FreePD (CC0, public domain)
    tracks = [
        ("Serenity", "https://freepd.com/music/Serenity.mp3", "ambient"),
        ("Floating", "https://freepd.com/music/Floating.mp3", "ambient"),
        ("Snowfall", "https://freepd.com/music/Snowfall.mp3", "ambient"),
        ("Healing", "https://freepd.com/music/Healing.mp3", "gentle"),
        ("Meditation", "https://freepd.com/music/Meditation.mp3", "ambient"),
        ("Weightless", "https://freepd.com/music/Weightless.mp3", "ambient"),
        ("Dreamy", "https://freepd.com/music/Dreamy.mp3", "lofi"),
        ("Peaceful", "https://freepd.com/music/Peaceful.mp3", "gentle"),
    ]
    
    for name, url, category in tracks[:max_tracks]:
        out_dir = OUT / category
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{name.lower()}.mp3"
        
        if out_path.exists():
            print(f"  {name}: cached", flush=True)
            downloaded.append({"id": name.lower(), "file": str(out_path.relative_to(REPO_ROOT)), "source": "freepd", "category": category})
            continue
        
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200 and len(resp.content) > 10000:
                out_path.write_bytes(resp.content)
                print(f"  {name}: OK ({len(resp.content)//1024}KB)", flush=True)
                downloaded.append({"id": name.lower(), "file": str(out_path.relative_to(REPO_ROOT)), "source": "freepd", "category": category})
            else:
                print(f"  {name}: failed ({resp.status_code})", flush=True)
        except Exception as e:
            print(f"  {name}: error ({e})", flush=True)
        time.sleep(0.5)
    
    return downloaded


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-tracks", type=int, default=50)
    args = ap.parse_args()
    
    all_tracks = []
    all_tracks.extend(download_freepd(args.max_tracks))
    
    print(f"\nDownloaded {len(all_tracks)} tracks total", flush=True)
