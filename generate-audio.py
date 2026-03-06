#!/usr/bin/env python3
"""Generate audio files for all karuta cards from karuta-data.json."""

from __future__ import annotations

import argparse
import asyncio
import json
import ssl
from pathlib import Path

try:
    import edge_tts
except ModuleNotFoundError as exc:
    raise SystemExit(
        "edge-tts is not installed. Install it with: pip install edge-tts"
    ) from exc


DEFAULT_DATA_FILE = Path("karuta-data.json")
DEFAULT_AUDIO_DIR = Path("audio")
DEFAULT_VOICE = "ja-JP-NanamiNeural"


ROMAJI_FALLBACK = {
    "あ": "a",
    "い": "i",
    "う": "u",
    "え": "e",
    "お": "o",
    "か": "ka",
    "き": "ki",
    "く": "ku",
    "け": "ke",
    "こ": "ko",
    "さ": "sa",
    "し": "shi",
    "す": "su",
    "せ": "se",
    "そ": "so",
    "た": "ta",
    "ち": "chi",
    "つ": "tsu",
    "て": "te",
    "と": "to",
    "な": "na",
    "に": "ni",
    "ぬ": "nu",
    "ね": "ne",
    "の": "no",
    "は": "ha",
    "ひ": "hi",
    "ふ": "fu",
    "へ": "he",
    "ほ": "ho",
    "ま": "ma",
    "み": "mi",
    "む": "mu",
    "め": "me",
    "も": "mo",
    "や": "ya",
    "ゆ": "yu",
    "よ": "yo",
    "ら": "ra",
    "り": "ri",
    "る": "ru",
    "れ": "re",
    "ろ": "ro",
    "わ": "wa",
    "を": "wo",
    "ん": "n",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate MP3s with edge-tts.")
    parser.add_argument(
        "--data",
        type=Path,
        default=DEFAULT_DATA_FILE,
        help="Path to karuta-data.json",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_AUDIO_DIR,
        help="Directory to write MP3 files",
    )
    parser.add_argument(
        "--voice",
        default=DEFAULT_VOICE,
        help="edge-tts voice ID (default: %(default)s)",
    )
    parser.add_argument(
        "--rate",
        default="+0%",
        help="Speech rate in edge-tts format (e.g. +10%, -5%)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing MP3 files",
    )
    parser.add_argument(
        "--no-verify-ssl",
        action="store_true",
        help="Disable SSL verification (for corporate proxies)",
    )
    return parser.parse_args()


async def generate_one(text: str, out_file: Path, voice: str, rate: str, overwrite: bool):
    if out_file.exists() and not overwrite:
        print(f"skip {out_file.name}: exists (use --overwrite to replace)")
        return
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    await communicate.save(str(out_file))


async def main() -> None:
    args = parse_args()
    with args.data.open("r", encoding="utf-8") as f:
        cards = json.load(f)

    if not isinstance(cards, list):
        raise SystemExit("karuta-data.json must be a list")

    if args.no_verify_ssl:
        _orig_create_default_context = ssl.create_default_context
        def _unverified_context(*a, **kw):
            ctx = _orig_create_default_context(*a, **kw)
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            return ctx
        ssl.create_default_context = _unverified_context

    args.out_dir.mkdir(parents=True, exist_ok=True)
    generated = 0

    for card in cards:
        text = str(card.get("sentence", "")).strip()
        if not text:
            print(f"skip: missing sentence for {card!r}")
            continue

        romaji = str(card.get("romaji", "")).strip() or ROMAJI_FALLBACK.get(card.get("hiragana", ""))
        if not romaji:
            print(f"skip: missing romaji for {card!r}")
            continue

        out_file = args.out_dir / f"{romaji}.mp3"
        await generate_one(text, out_file, args.voice, args.rate, args.overwrite)
        generated += 1
        print(f"generated: {out_file.name}")

    print(f"done: {generated}/{len(cards)} files requested")


if __name__ == "__main__":
    asyncio.run(main())
