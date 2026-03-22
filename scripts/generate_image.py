#!/usr/bin/env python3
"""Generate images via Gemini API (Imagen 4.0 or Gemini Flash Image).

Usage:
    uv run scripts/generate_image.py "a blue circle on white background"
    uv run scripts/generate_image.py "a blue circle" --output /tmp/circle.png
    uv run scripts/generate_image.py "a blue circle" --model imagen  # imagen-4.0-generate-001
    uv run scripts/generate_image.py "a blue circle" --model flash   # gemini-2.5-flash-image
    uv run scripts/generate_image.py "edit: make it red" --input /tmp/circle.png  # image editing
"""

import argparse
import base64
import json
import os
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("Installing requests...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests


def get_api_key():
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key
    # Try loading from .env files
    for env_path in [
        Path(__file__).parent.parent / ".env",
        Path.cwd() / ".env",
        Path.home() / "workspace/skywalking/.env",
        Path.home() / "workspace/skywalking/hive/.env",
    ]:
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith("GEMINI_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    print("Error: GEMINI_API_KEY not found. Set it in .env or environment.", file=sys.stderr)
    sys.exit(1)


def generate_with_imagen(prompt: str, api_key: str, output: str, model: str = "imagen-4.0-generate-001"):
    """Generate image using Imagen 4.0 (predict endpoint)."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:predict?key={api_key}"
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": "1:1",
        },
    }
    resp = requests.post(url, json=payload, timeout=60)
    data = resp.json()

    if "error" in data:
        print(f"Error: {data['error']['message']}", file=sys.stderr)
        sys.exit(1)

    predictions = data.get("predictions", [])
    if not predictions:
        print("Error: No image generated", file=sys.stderr)
        sys.exit(1)

    img_b64 = predictions[0].get("bytesBase64Encoded")
    if not img_b64:
        print("Error: No image data in response", file=sys.stderr)
        sys.exit(1)

    img_bytes = base64.b64decode(img_b64)
    Path(output).write_bytes(img_bytes)
    print(f"Saved: {output} ({len(img_bytes)} bytes)")
    return output


def generate_with_flash(prompt: str, api_key: str, output: str, input_image: str | None = None, model: str = "gemini-2.5-flash-image"):
    """Generate/edit image using Gemini Flash Image (generateContent endpoint)."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    parts = []
    if input_image:
        img_bytes = Path(input_image).read_bytes()
        img_b64 = base64.b64encode(img_bytes).decode()
        mime = "image/png" if input_image.endswith(".png") else "image/jpeg"
        parts.append({"inlineData": {"mimeType": mime, "data": img_b64}})

    parts.append({"text": prompt})

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
    }
    resp = requests.post(url, json=payload, timeout=120)
    data = resp.json()

    if "error" in data:
        print(f"Error: {data['error']['message']}", file=sys.stderr)
        sys.exit(1)

    candidates = data.get("candidates", [])
    if not candidates:
        print("Error: No candidates in response", file=sys.stderr)
        sys.exit(1)

    for part in candidates[0]["content"]["parts"]:
        if "inlineData" in part:
            img_bytes = base64.b64decode(part["inlineData"]["data"])
            Path(output).write_bytes(img_bytes)
            print(f"Saved: {output} ({len(img_bytes)} bytes)")
            return output
        if "text" in part:
            print(f"Model: {part['text'][:200]}")

    print("Error: No image in response", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Generate images via Gemini API")
    parser.add_argument("prompt", help="Image description / prompt")
    parser.add_argument("--output", "-o", default=None, help="Output path (default: /tmp/generated_image.png)")
    parser.add_argument("--model", "-m", default="imagen", choices=["imagen", "flash", "pro", "banana2"], help="Model: imagen (4.0), flash (nano banana), pro (nano banana pro), banana2 (3.1 flash image)")
    parser.add_argument("--input", "-i", default=None, help="Input image for editing (flash model only)")
    parser.add_argument("--aspect", "-a", default="1:1", help="Aspect ratio for Imagen (1:1, 16:9, 9:16, 4:3, 3:4)")
    args = parser.parse_args()

    api_key = get_api_key()
    output = args.output or "/tmp/generated_image.png"

    model_map = {
        "flash": "gemini-2.5-flash-image",
        "pro": "gemini-3-pro-image-preview",
        "banana2": "gemini-3.1-flash-image-preview",
    }

    if args.model in model_map or args.input:
        model_name = model_map.get(args.model, "gemini-2.5-flash-image")
        generate_with_flash(args.prompt, api_key, output, args.input, model_name)
    else:
        generate_with_imagen(args.prompt, api_key, output)


if __name__ == "__main__":
    main()
