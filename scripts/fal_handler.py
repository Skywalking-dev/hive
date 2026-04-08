#!/usr/bin/env python3
"""fal.ai handler for Hive.
Image + video generation via unified REST API.
Supports FLUX, Ideogram, Recraft (image) and Kling, Veo, Hailuo (video).
"""
import json
import os
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

# Load .env
SCRIPT_DIR = Path(__file__).resolve().parent
HIVE_DIR = SCRIPT_DIR.parent
env_path = HIVE_DIR / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

FAL_KEY = os.environ.get("FAL_KEY", "")
if not FAL_KEY:
    print(json.dumps({"success": False, "error": "FAL_KEY not set"}), file=sys.stderr)
    sys.exit(1)

QUEUE_URL = "https://queue.fal.run"
SYNC_URL = "https://fal.run"

# Model aliases
IMAGE_MODELS = {
    "schnell": "fal-ai/flux/schnell",
    "flux-pro": "fal-ai/flux-pro/v1.1",
    "flux-ultra": "fal-ai/flux-pro/v1.1-ultra",
    "ideogram": "fal-ai/ideogram/v2",
    "recraft": "fal-ai/recraft/v3/text-to-image",
}

VIDEO_MODELS = {
    "wan": "fal-ai/wan/v2.7/text-to-video",
    "wan-i2v": "fal-ai/wan/v2.7/image-to-video",
    "kling": "fal-ai/kling-video/v2.5-turbo/pro/text-to-video",
    "kling-i2v": "fal-ai/kling-video/v2.5-turbo/pro/image-to-video",
    "kling3": "fal-ai/kling-video/v3/pro/image-to-video",
    "veo": "fal-ai/veo3.1/lite/text-to-video",
    "veo-fast": "fal-ai/veo3.1/fast/text-to-video",
    "veo-std": "fal-ai/veo3.1/text-to-video",
    "sora": "fal-ai/sora-2/text-to-video",
    "pixverse": "fal-ai/pixverse/v6/text-to-video",
}


def api_request(url: str, payload: dict | None = None, method: str = "POST") -> dict:
    headers = {
        "Authorization": f"Key {FAL_KEY}",
        "Content-Type": "application/json",
    }
    data = json.dumps(payload).encode() if payload else None
    req = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=300) as resp:
            return json.loads(resp.read())
    except HTTPError as e:
        body = e.read().decode()
        try:
            return json.loads(body)
        except Exception:
            return {"error": body, "status": e.code}


def poll_until_done(model_id: str, request_id: str, max_wait: int = 300) -> dict:
    status_url = f"{QUEUE_URL}/{model_id}/requests/{request_id}/status"
    result_url = f"{QUEUE_URL}/{model_id}/requests/{request_id}"
    elapsed = 0
    interval = 3
    while elapsed < max_wait:
        status = api_request(f"{status_url}?logs=1", method="GET")
        s = status.get("status", "")
        if s == "COMPLETED":
            return api_request(result_url, method="GET")
        if s in ("FAILED", "CANCELLED"):
            return {"error": f"Job {s}", "detail": status}
        time.sleep(interval)
        elapsed += interval
        if elapsed > 30:
            interval = 5
    return {"error": f"Timeout after {max_wait}s"}


def cmd_image(args: list[str]):
    prompt = ""
    model = "schnell"
    size = "landscape_4_3"
    num = 1
    style = None

    i = 0
    while i < len(args):
        if args[i] == "--model" and i + 1 < len(args):
            model = args[i + 1]; i += 2
        elif args[i] == "--size" and i + 1 < len(args):
            size = args[i + 1]; i += 2
        elif args[i] == "--num" and i + 1 < len(args):
            num = int(args[i + 1]); i += 2
        elif args[i] == "--style" and i + 1 < len(args):
            style = args[i + 1]; i += 2
        else:
            prompt = args[i]; i += 1

    if not prompt:
        print("Usage: image <prompt> [--model schnell|flux-pro|ideogram|recraft] [--size S] [--num N]")
        sys.exit(1)

    model_id = IMAGE_MODELS.get(model, model)
    payload = {"prompt": prompt, "num_images": num}

    if "ideogram" in model_id:
        payload["aspect_ratio"] = size.replace("_", ":")
        if style:
            payload["style"] = style
    elif "recraft" in model_id:
        payload["image_size"] = size
        if style:
            payload["style"] = style
    else:
        payload["image_size"] = size

    # schnell is fast enough for sync
    if model in ("schnell",):
        result = api_request(f"{SYNC_URL}/{model_id}", payload)
    else:
        submit = api_request(f"{QUEUE_URL}/{model_id}", payload)
        if "error" in submit:
            print(json.dumps({"success": False, "error": submit}))
            return
        request_id = submit["request_id"]
        print(f"Queued: {request_id}", file=sys.stderr)
        result = poll_until_done(model_id, request_id)

    if "error" in result:
        print(json.dumps({"success": False, "error": result}))
        return

    images = result.get("images", [])
    print(json.dumps({
        "success": True,
        "data": {
            "type": "image",
            "model": model_id,
            "images": [{"url": img["url"], "width": img.get("width"), "height": img.get("height")} for img in images],
            "seed": result.get("seed"),
        }
    }, indent=2))


def cmd_video(args: list[str]):
    prompt = ""
    model = "wan"
    duration = "5"
    aspect = "16:9"

    i = 0
    while i < len(args):
        if args[i] == "--model" and i + 1 < len(args):
            model = args[i + 1]; i += 2
        elif args[i] == "--duration" and i + 1 < len(args):
            duration = args[i + 1]; i += 2
        elif args[i] == "--aspect" and i + 1 < len(args):
            aspect = args[i + 1]; i += 2
        else:
            prompt = args[i]; i += 1

    if not prompt:
        print("Usage: video <prompt> [--model kling|veo|hailuo] [--duration 5] [--aspect 16:9]")
        sys.exit(1)

    model_id = VIDEO_MODELS.get(model, model)
    payload = {"prompt": prompt, "aspect_ratio": aspect}

    # Duration format varies by provider
    if "veo" in model_id:
        payload["duration"] = f"{duration}s"
    elif "kling" in model_id:
        payload["duration"] = duration  # string
    else:
        payload["duration"] = int(duration)  # wan, sora, pixverse use int

    submit = api_request(f"{QUEUE_URL}/{model_id}", payload)
    if "error" in submit:
        print(json.dumps({"success": False, "error": submit}))
        return

    request_id = submit["request_id"]
    print(f"Queued: {request_id} (video gen takes 30-120s)", file=sys.stderr)
    result = poll_until_done(model_id, request_id, max_wait=300)

    if "error" in result:
        print(json.dumps({"success": False, "error": result}))
        return

    video = result.get("video", {})
    print(json.dumps({
        "success": True,
        "data": {
            "type": "video",
            "model": model_id,
            "url": video.get("url", ""),
            "content_type": video.get("content_type", "video/mp4"),
            "file_size": video.get("file_size"),
        }
    }, indent=2))


def cmd_status(args: list[str]):
    if len(args) < 2:
        print("Usage: status <model-alias-or-id> <request-id>")
        sys.exit(1)
    model = args[0]
    request_id = args[1]
    model_id = IMAGE_MODELS.get(model, VIDEO_MODELS.get(model, model))
    status_url = f"{QUEUE_URL}/{model_id}/requests/{request_id}/status?logs=1"
    result = api_request(status_url, method="GET")
    print(json.dumps(result, indent=2))


def cmd_models(_args: list[str]):
    print(json.dumps({
        "image": IMAGE_MODELS,
        "video": VIDEO_MODELS,
    }, indent=2))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: fal_handler.py <image|video|status|models> [args]")
        sys.exit(1)

    command = sys.argv[1]
    rest = sys.argv[2:]

    commands = {
        "image": cmd_image,
        "video": cmd_video,
        "status": cmd_status,
        "models": cmd_models,
    }

    if command not in commands:
        print(f"Unknown command: {command}. Use: {', '.join(commands.keys())}")
        sys.exit(1)

    commands[command](rest)
