"""Fetch YouTube transcripts (auto-generated or manual) into the raw layer.

Dependency: youtube-transcript-api  (pip install youtube-transcript-api)
Output: sources/docs/community/youtube/<video_id>.transcript.txt

Usage:
  python scripts/fetch_youtube_transcript.py 2mMtLycHK-4 [more-video-ids...]
  python scripts/fetch_youtube_transcript.py --video-url https://www.youtube.com/watch?v=2mMtLycHK-4
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "sources" / "docs" / "community" / "youtube"
LANGUAGES = ["zh-Hans", "zh", "en"]


def fetch(video_id: str) -> Path:
    from youtube_transcript_api import YouTubeTranscriptApi

    api = YouTubeTranscriptApi()
    transcript = None
    used_lang = ""
    for lang in LANGUAGES:
        try:
            transcript = api.fetch(video_id, languages=[lang])
            used_lang = lang
            break
        except Exception:  # noqa: BLE001
            continue
    if transcript is None:
        raise RuntimeError(f"no transcript found for {video_id}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    lines = [f"# video_id: {video_id}", f"# language: {used_lang}", "#"]
    for seg in transcript.snippets:
        lines.append(f"[{seg.start:.1f}] {seg.text}")
    target = OUT_DIR / f"{video_id}.transcript.txt"
    target.write_text("\n".join(lines), encoding="utf-8")
    print(f"saved {target} ({len(transcript.snippets)} segments, lang={used_lang})")
    return target


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*", help="YouTube video IDs")
    ap.add_argument("--video-url", help="full watch URL")
    args = ap.parse_args()
    ids = list(args.ids)
    if args.video_url:
        m = re.search(r"[?&]v=([A-Za-z0-9_-]{11})", args.video_url)
        if m:
            ids.append(m.group(1))
    if not ids:
        ap.print_help()
        return 2
    for vid in ids:
        try:
            fetch(vid)
        except Exception as exc:  # noqa: BLE001
            print(f"FAIL {vid}: {exc}")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
