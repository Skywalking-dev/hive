---
name: generate_image
description: Generate images via Gemini API (Imagen 4.0 or Gemini Flash). Use when user needs to create, edit, or transform images. Supports text-to-image and image editing with input reference.
allowed-tools: Bash(uv run:*), Bash(GEMINI_API_KEY=*), Bash(open:*), Read
---

# Generate Image

Create and edit images via Gemini API.

## Models

| Model | Flag | Best For | Editing |
|-------|------|----------|---------|
| Imagen 4.0 | `-m imagen` (default) | Text-to-image, artistic, brand assets | No |
| Nano Banana | `-m flash` | Cosmetic edits, color changes, style tweaks | Yes (`-i`) |
| Nano Banana Pro | `-m pro` | **Sketch-to-render, structural accuracy, technical diagrams** | Yes (`-i`) |
| Nano Banana 2 | `-m banana2` | Experimental | Yes (`-i`) |

## Usage

```bash
# Text to image (Imagen 4.0)
GEMINI_API_KEY={key} uv run scripts/generate_image.py "prompt" -o /path/to/output.png

# With aspect ratio
GEMINI_API_KEY={key} uv run scripts/generate_image.py "prompt" -a 16:9 -o /path/to/output.png

# Edit existing image (Flash — cosmetic only)
GEMINI_API_KEY={key} uv run scripts/generate_image.py "make the background red" -m flash -i /path/to/input.png -o /path/to/output.png

# Sketch-to-render (Pro — structural accuracy)
GEMINI_API_KEY={key} uv run scripts/generate_image.py "render as photorealistic 3D" -m pro -i /path/to/sketch.jpg -o /path/to/output.png

# Iterative refinement (Pro — on previous render)
GEMINI_API_KEY={key} uv run scripts/generate_image.py "make it taller and narrower" -m pro -i /path/to/previous.png -o /path/to/output.png
```

## Handler

`scripts/generate_image.py` — standalone Python script, only needs `requests`.

## Decision Tree

```
What kind of image?
│
├─ Artistic / brand / conceptual
│  └─ Use: imagen (default)
│
├─ Technical / structural / construction / diagram
│  ├─ User has a sketch? → Pro + sketch as input (BEST PATH)
│  ├─ No sketch? → Ask user to draw one (even rough paper sketch)
│  └─ NEVER rely on text-only for precise structural details
│
├─ Edit existing image
│  ├─ Cosmetic change (color, texture, remove element) → Flash
│  └─ Structural change (add/remove parts, reshape) → Pro
│
└─ Refine proportions / style of existing render
   └─ Pro + previous render as input
```

## Prompting Rules

### Do
- **Describe what is VISIBLE from the camera angle**, not how it's built
- **Use analogies for shapes** ("like a picture frame", "like a bookshelf") — models understand objects, not specs
- **Affirm what exists** ("has 2 horizontal bars") instead of negating ("NO vertical bars")
- **One fix per iteration** — single change requests produce reliable results
- **Set aspect ratio explicitly** (`-a 9:16` for tall, `-a 16:9` for wide)
- **Separate structure from aesthetics** — get the shape right first, then refine lighting/realism

### Don't
- **Never use negations** ("NO", "ZERO", "WITHOUT", "NEVER") — models ignore or invert them
- **Never ask for text/labels in the image** — Gemini renders text poorly. Add labels with PIL/Pillow after
- **Never pass 3 text-only attempts** for structural images — if 3 fail, change strategy (get sketch, use reference image, try different analogy)
- **Never use Flash for structural edits** — it only handles cosmetic changes
- **Never use ALL CAPS emphasis** ("CRITICAL", "IMPORTANT") — it doesn't improve accuracy

### Prompt Structure (text-only)
```
[Photo style] + [Object description using familiar analogy] +
[What is visible from this angle] + [Materials/textures] +
[Background/lighting] + "no text"
```

### Prompt Structure (sketch-to-render)
```
"Transform this sketch into [style]. Keep the EXACT same structure.
[Material descriptions]. [Lighting/background]. No text."
```

### Prompt Structure (iterative refinement)
```
"[Single specific change]. Keep everything else exactly the same."
```

## Workflow: Technical/Construction Images

```
Step 1: Ask user for a hand-drawn sketch (paper, tablet, anything)
Step 2: Copy sketch to /tmp/ (handle unicode filenames)
Step 3: Pro + sketch → first render
Step 4: Review with user → identify ONE issue
Step 5: Pro + previous render → fix that one issue
Step 6: Repeat 4-5 until correct (usually 2-3 iterations)
Step 7: Save final to project assets
```

**Budget: max 5-6 calls total. If not converging, re-examine the sketch or prompt strategy.**

## Anti-patterns (learned from experience)

| Anti-pattern | Why it fails | Do instead |
|---|---|---|
| "ZERO vertical bars" | Models ignore negations | "Only horizontal bars" |
| "CRITICAL: exactly 4 pieces" | Emphasis doesn't control count | Use sketch as input |
| 20+ text-only iterations | Diminishing returns after attempt 3 | Get a sketch, research techniques |
| Flash for structural edits | Flash only does cosmetic changes | Use Pro for structure |
| Labels in the render | Gemini misspells, misplaces text | Generate clean, label with PIL |
| Multiple fixes per iteration | Model applies some, ignores others | One change at a time |
| Describing construction process | Model doesn't understand "screwed to" | Describe visual composition |

## Rules

- Always run from `hive/` directory
- Default output: `/tmp/generated_image.png`
- **ALWAYS open the image after generating:** `open /path/to/output.png`
- **ALWAYS read the image after opening** to verify result before responding
- For brand assets, reference `docs/PRODUCT_IDENTITY.md` for colors and style
- Imagen has content safety filters — if blocked, rephrase the prompt
- Handle macOS unicode filenames (narrow no-break space `\u202f`) when copying user photos
