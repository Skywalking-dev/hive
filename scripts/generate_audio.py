#!/usr/bin/env python3
"""Generate speech via OpenAI TTS API — Mentat's voice.

Usage:
    uv run scripts/generate_audio.py "Hola, soy Mentat."
    uv run scripts/generate_audio.py "Hello, I am Mentat." --voice onyx --lang en
    uv run scripts/generate_audio.py --file /tmp/briefing.txt -o /tmp/briefing.mp3
    echo "Quick note" | uv run scripts/generate_audio.py --stdin
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests

# Mentat voice config
MENTAT_VOICE = {
    "es": "onyx",
    "en": "onyx",
}

MENTAT_INSTRUCTIONS = {
    "es": "Speak in clear Latin American Spanish. Tone: serious but warm, like a trusted strategic advisor. Cadence: deliberate, slightly faster than normal. Emotion: confident and grounded. Accent: neutral Latin American, no Spain. Style: like a senior consultant giving a private briefing.",
    "en": "Speak in British English. Tone: serious but warm, like a trusted strategic advisor. Cadence: deliberate, slightly faster than normal. Emotion: confident and grounded. Style: like a senior consultant giving a private briefing.",
}

VALID_VOICES = ["alloy", "ash", "ballad", "coral", "echo", "fable", "nova", "onyx", "sage", "shimmer"]
VALID_FORMATS = ["mp3", "opus", "aac", "flac", "wav", "pcm"]


def get_api_key():
    key = os.environ.get("OPENAI_API_KEY")
    if key:
        return key
    for env_path in [
        Path(__file__).parent.parent / ".env",
        Path.cwd() / ".env",
        Path.home() / "workspace/skywalking/.env",
        Path.home() / "workspace/skywalking/hive/.env",
    ]:
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith("OPENAI_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    print("Error: OPENAI_API_KEY not found. Set it in .env or environment.", file=sys.stderr)
    sys.exit(1)


def generate_speech(
    text: str,
    api_key: str,
    output: str,
    voice: str = "onyx",
    model: str = "tts-1-hd",
    fmt: str = "mp3",
    speed: float = 1.0,
    instructions: str | None = None,
):
    """Generate speech from text via OpenAI TTS API."""
    url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "input": text,
        "voice": voice,
        "response_format": fmt,
        "speed": speed,
    }
    if instructions:
        payload["instructions"] = instructions

    resp = requests.post(url, headers=headers, json=payload, timeout=120)

    if resp.status_code != 200:
        try:
            err = resp.json()
            msg = err.get("error", {}).get("message", resp.text)
        except Exception:
            msg = resp.text
        print(f"Error ({resp.status_code}): {msg}", file=sys.stderr)
        sys.exit(1)

    Path(output).write_bytes(resp.content)
    print(f"Saved: {output} ({len(resp.content)} bytes, {voice}/{model}/{fmt})")
    return output


def play_audio(path: str):
    """Play audio file on macOS."""
    if sys.platform == "darwin":
        subprocess.Popen(["afplay", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Playing: {path}")
    else:
        print(f"Auto-play not supported on {sys.platform}. Open manually: {path}")


def main():
    parser = argparse.ArgumentParser(description="Generate speech via OpenAI TTS — Mentat's voice")
    parser.add_argument("text", nargs="?", default=None, help="Text to speak")
    parser.add_argument("--file", "-f", default=None, help="Read text from file")
    parser.add_argument("--stdin", action="store_true", help="Read text from stdin")
    parser.add_argument("--output", "-o", default=None, help="Output path (default: /tmp/mentat_speech.mp3)")
    parser.add_argument("--voice", "-v", default=None, choices=VALID_VOICES, help="Voice (default: Mentat's voice)")
    parser.add_argument("--model", "-m", default="gpt-4o-mini-tts", choices=["tts-1", "tts-1-hd", "gpt-4o-mini-tts"], help="Model: tts-1 (fast), tts-1-hd (quality), gpt-4o-mini-tts (expressive, default)")
    parser.add_argument("--lang", "-l", default="es", choices=["es", "en"], help="Language hint for default voice and instructions (es/en)")
    parser.add_argument("--format", default="mp3", choices=VALID_FORMATS, help="Output format")
    parser.add_argument("--speed", "-s", type=float, default=1.15, help="Speed 0.25-4.0 (default: 1.15)")
    parser.add_argument("--instructions", default=None, help="Voice style instructions (gpt-4o-mini-tts only, overrides default Mentat instructions)")
    parser.add_argument("--no-play", action="store_true", help="Don't auto-play after generating")
    parser.add_argument("--samples", action="store_true", help="Generate samples with all voices for comparison")
    args = parser.parse_args()

    # Resolve text input
    if args.samples:
        text = args.text or "Hola. Soy Mentat, tu consejero estratégico. Analicemos la situación."
    elif args.stdin:
        text = sys.stdin.read().strip()
    elif args.file:
        text = Path(args.file).read_text().strip()
    elif args.text:
        text = args.text
    else:
        parser.error("Provide text, --file, or --stdin")

    if not text:
        print("Error: empty text", file=sys.stderr)
        sys.exit(1)

    # TTS has a 4096 char limit per request
    if len(text) > 4096:
        print(f"Warning: text is {len(text)} chars, truncating to 4096", file=sys.stderr)
        text = text[:4096]

    api_key = get_api_key()

    # Sample mode — generate all voices for comparison
    if args.samples:
        out_dir = Path("/tmp/mentat_voice_samples")
        out_dir.mkdir(exist_ok=True)
        print(f"Generating voice samples in {out_dir}/")
        for voice in VALID_VOICES:
            out_path = str(out_dir / f"{voice}.mp3")
            generate_speech(text, api_key, out_path, voice=voice, model="tts-1-hd")
        print(f"\nAll samples saved to {out_dir}/")
        print("Play them with: afplay /tmp/mentat_voice_samples/<voice>.mp3")
        return

    # Resolve voice and instructions — explicit flags > Mentat defaults
    voice = args.voice or MENTAT_VOICE.get(args.lang, "onyx")
    instructions = args.instructions or MENTAT_INSTRUCTIONS.get(args.lang)
    output = args.output or "/tmp/mentat_speech.mp3"

    generate_speech(
        text=text,
        api_key=api_key,
        output=output,
        voice=voice,
        model=args.model,
        fmt=args.format,
        speed=args.speed,
        instructions=instructions,
    )

    if not args.no_play:
        play_audio(output)


if __name__ == "__main__":
    main()
