#!/usr/bin/env python3
"""Telegram bot for sketch-to-render image generation via Gemini Pro.

Send a photo (sketch) with a caption describing what you want, and get back
a photorealistic render. Uses Gemini Pro (sketch-to-render) which is the most
reliable model for preserving structural details from hand-drawn sketches.

Usage:
    TELEGRAM_BOT_TOKEN=xxx GEMINI_API_KEY=xxx uv run scripts/telegram_sketch_bot.py

Env vars:
    TELEGRAM_BOT_TOKEN — Telegram Bot API token (from @BotFather)
    GEMINI_API_KEY — Google Gemini API key

How to use the bot:
    1. Send a photo of a hand-drawn sketch
    2. Add a caption describing the render you want (or omit for default)
    3. Wait ~15-30 seconds for the render
    4. Reply to the result with "fix: <what to change>" to iterate
"""

import base64
import io
import logging
import os
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests

try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-telegram-bot", "-q"])
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

DEFAULT_PROMPT = "Transform this hand-drawn sketch into a clean photorealistic 3D render. Keep the EXACT same structure shown in the sketch. Gray background, studio lighting, photorealistic, no text."

MODELS = {
    "pro": "gemini-3-pro-image-preview",
    "flash": "gemini-2.5-flash-image",
    "imagen": "imagen-4.0-generate-001",
}


def get_env(key: str) -> str:
    val = os.environ.get(key)
    if val:
        return val
    for env_path in [
        Path(__file__).parent.parent / ".env",
        Path.home() / "workspace/skywalking/hive/.env",
    ]:
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith(f"{key}="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    print(f"Error: {key} not found", file=sys.stderr)
    sys.exit(1)


def gemini_generate(prompt: str, api_key: str, input_image: bytes | None = None, model: str = "pro") -> bytes | None:
    """Generate image via Gemini API. Returns image bytes or None."""
    model_id = MODELS.get(model, MODELS["pro"])
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={api_key}"

    parts = []
    if input_image:
        img_b64 = base64.b64encode(input_image).decode()
        parts.append({"inlineData": {"mimeType": "image/jpeg", "data": img_b64}})
    parts.append({"text": prompt})

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
    }

    resp = requests.post(url, json=payload, timeout=120)
    data = resp.json()

    if "error" in data:
        log.error("Gemini error: %s", data["error"].get("message", data["error"]))
        return None

    candidates = data.get("candidates", [])
    if not candidates:
        log.error("No candidates in response")
        return None

    text_response = ""
    for part in candidates[0]["content"]["parts"]:
        if "inlineData" in part:
            return base64.b64decode(part["inlineData"]["data"])
        if "text" in part:
            text_response = part["text"]

    if text_response:
        log.info("Model text response: %s", text_response[:200])
    return None


# --- Telegram handlers ---

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Sketch → Render Bot\n\n"
        "Envio una foto de un sketch y te devuelvo un render fotorrealista.\n\n"
        "Modos:\n"
        "- Foto + caption = sketch-to-render con tu prompt\n"
        "- Foto sin caption = render con prompt default\n"
        "- Reply a un render con 'fix: ...' = iterar sobre el resultado\n\n"
        "Modelos: /pro (default), /flash, /imagen\n"
        "Aspect ratio: agrega 16:9, 9:16, etc al caption"
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await cmd_start(update, context)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming photo (sketch) — generate render."""
    api_key = get_env("GEMINI_API_KEY")
    msg = update.message

    # Get the largest photo
    photo = msg.photo[-1]
    file = await photo.get_file()
    img_bytes = await file.download_as_bytearray()

    # Get prompt from caption or default
    caption = msg.caption or ""
    prompt = caption.strip() if caption.strip() else DEFAULT_PROMPT

    # Check for model override in caption
    model = "pro"
    for m in ["flash", "imagen", "pro"]:
        if f"/{m}" in prompt.lower():
            model = m
            prompt = prompt.replace(f"/{m}", "").strip()

    # Send "generating..." status
    status_msg = await msg.reply_text(f"Generando render ({model})...")

    # Generate
    result = gemini_generate(prompt, api_key, bytes(img_bytes), model)

    try:
        if result:
            context.user_data["last_render"] = result
            context.user_data["last_prompt"] = prompt
            await msg.reply_photo(
                photo=io.BytesIO(result),
                caption=f"Render ({model}) — reply con 'fix: ...' para iterar"
            )
            await status_msg.delete()
        else:
            await status_msg.edit_text("Error generando imagen. Intenta con otro prompt o modelo.")
    except Exception:
        await status_msg.edit_text("Error procesando resultado.")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages — iterate on previous render or generate from text."""
    api_key = get_env("GEMINI_API_KEY")
    msg = update.message
    text = msg.text.strip()

    # Check if replying to a render (iteration)
    if msg.reply_to_message and msg.reply_to_message.photo:
        # Get the photo being replied to
        photo = msg.reply_to_message.photo[-1]
        file = await photo.get_file()
        img_bytes = await file.download_as_bytearray()

        model = "pro"
        prompt = text
        if prompt.lower().startswith("fix:"):
            prompt = prompt[4:].strip()
        prompt = f"{prompt}. Keep everything else exactly the same."

        status_msg = await msg.reply_text(f"Iterando ({model})...")

        result = gemini_generate(prompt, api_key, bytes(img_bytes), model)

        try:
            if result:
                context.user_data["last_render"] = result
                await msg.reply_photo(
                    photo=io.BytesIO(result),
                    caption=f"Iteración ({model}) — reply con 'fix: ...' para seguir"
                )
                await status_msg.delete()
            else:
                await status_msg.edit_text("Error en iteración.")
        except Exception:
            await status_msg.edit_text("Error procesando iteración.")
        return

    # Check if there's a previous render to iterate on
    last_render = context.user_data.get("last_render")
    if last_render and (text.lower().startswith("fix:") or text.lower().startswith("ajusta")):
        prompt = text.split(":", 1)[1].strip() if ":" in text else text
        prompt = f"{prompt}. Keep everything else exactly the same."

        status_msg = await msg.reply_text("Iterando sobre el ultimo render...")
        result = gemini_generate(prompt, api_key, last_render, "pro")

        try:
            if result:
                context.user_data["last_render"] = result
                await msg.reply_photo(
                    photo=io.BytesIO(result),
                    caption="Iteración — reply con 'fix: ...' para seguir"
                )
                await status_msg.delete()
            else:
                await status_msg.edit_text("Error en iteración.")
        except Exception:
            await status_msg.edit_text("Error procesando iteración.")
        return

    # Text-only generation (no sketch)
    status_msg = await msg.reply_text("Generando desde texto...")
    result = gemini_generate(text, api_key, model="pro")

    try:
        if result:
            context.user_data["last_render"] = result
            await msg.reply_photo(
                photo=io.BytesIO(result),
                caption="Render — reply con 'fix: ...' para iterar"
            )
            await status_msg.delete()
        else:
            await status_msg.edit_text("Error generando imagen.")
    except Exception:
        await status_msg.edit_text("Error procesando resultado.")


def main():
    token = get_env("TELEGRAM_BOT_TOKEN")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    log.info("Bot started. Waiting for messages...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
