---
name: generate_image
description: Generate images via Gemini API (Imagen 4.0 or Gemini Flash). Use when user needs to create, edit, or transform images. Supports text-to-image and image editing with input reference.
allowed-tools: Bash(uv run:*), Bash(GEMINI_API_KEY=*), Bash(open:*), Read
---

# Generate Image

Create and edit images via Gemini API.

## Models

| Model | Best For | Editing |
|-------|----------|---------|
| `imagen` (default) | Text-to-image, high quality | No |
| `flash` | Image editing, variations, context-aware | Yes (with --input) |

## Usage

```bash
# Text to image (Imagen 4.0)
GEMINI_API_KEY={key} uv run scripts/generate_image.py "prompt" -o /path/to/output.png

# With aspect ratio
GEMINI_API_KEY={key} uv run scripts/generate_image.py "prompt" -a 16:9 -o /path/to/output.png

# Edit existing image (Flash)
GEMINI_API_KEY={key} uv run scripts/generate_image.py "make the background red" -m flash -i /path/to/input.png -o /path/to/output.png
```

## Handler

`scripts/generate_image.py` — standalone Python script, only needs `requests`.

## Models

```bash
-m imagen   # Imagen 4.0 (default, best quality)
-m flash    # Nano Banana (gemini-2.5-flash-image, editing)
-m pro      # Nano Banana Pro (gemini-3-pro-image-preview)
-m banana2  # Nano Banana 2 (gemini-3.1-flash-image-preview)
```

## Rules

- Always run from `hive/` directory
- Default output: `/tmp/generated_image.png`
- **ALWAYS open the image after generating:** `open /path/to/output.png`
- For brand assets, reference `docs/PRODUCT_IDENTITY.md` for colors and style
- Imagen has content safety filters — if blocked, rephrase the prompt
