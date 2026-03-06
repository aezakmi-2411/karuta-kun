#!/usr/bin/env python3
"""Generate audio files using VOICEVOX CLI."""

import argparse
import asyncio
import json
import subprocess
from pathlib import Path

DEFAULT_DATA_FILE = Path("karuta-data.json")
DEFAULT_AUDIO_DIR = Path("audio-voicevox")
# Speaker 11: Kurono Takehiro (Cool/Calm Male)
DEFAULT_SPEAKER = "11" 

def parse_args():
    parser = argparse.ArgumentParser(description="Generate MP3s with Voicevox CLI.")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA_FILE)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_AUDIO_DIR)
    parser.add_argument("--speaker", default=DEFAULT_SPEAKER, help="Voicevox Speaker ID")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()

async def generate_one(text: str, out_file: Path, speaker: str, overwrite: bool):
    if out_file.exists() and not overwrite:
        return

    # voicevox-cli generates WAV. We can use it directly or convert to MP3.
    # Command: voicevox speak "text" --speaker 11 --output "path.wav"
    cmd = [
        "voicevox", "speak",
        text,
        "--speaker", speaker,
        "--output", str(out_file)
    ]
    
    try:
        # Use shell=True for Windows command resolution if needed
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            print(f"Error generating {out_file.name}: {stderr.decode()}")
        else:
            print(f"Generated: {out_file.name}")
    except Exception as e:
        print(f"Failed to run voicevox-cli: {e}")

async def main():
    args = parse_args()
    with args.data.open("r", encoding="utf-8") as f:
        cards = json.load(f)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Starting Voicevox generation using Speaker ID: {args.speaker}")
    print("Ensure VOICEVOX Engine is running at http://localhost:50021")

    tasks = []
    for card in cards:
        text = card["sentence"]
        romaji = card["romaji"]
        out_file = args.out_dir / f"{romaji}.wav"
        tasks.append(generate_one(text, out_file, args.speaker, args.overwrite))
    
    await asyncio.gather(*tasks)
    print("Done.")

if __name__ == "__main__":
    asyncio.run(main())
