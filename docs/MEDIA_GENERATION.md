# Media Generation — Image & Video

> Hive capabilities for visual content generation.
> Last updated: 2026-04-08

---

## Handlers

| Handler | API | Media | Env Key |
|---------|-----|-------|---------|
| `scripts/generate_image.py` | Gemini (Imagen 4.0, Flash, Nano Banana) | Image | `GEMINI_API_KEY` |
| `scripts/fal_handler.py` | fal.ai (FLUX, Ideogram, Recraft, Wan, Kling, Veo, Sora) | Image + Video | `FAL_KEY` |

---

## Image Generation

### generate_image.py (Gemini)

Genera y edita imagenes via Gemini API. Gratis en free tier.

```bash
# Imagen 4.0 — mejor fotorrealismo
uv run scripts/generate_image.py "product shot of a coffee cup" --model imagen

# Gemini Flash (Nano Banana) — conversacional, edicion
uv run scripts/generate_image.py "a minimalist logo for a tech company" --model flash

# Gemini Pro (Nano Banana Pro)
uv run scripts/generate_image.py "watercolor landscape" --model pro

# Edicion de imagen existente (solo flash/pro)
uv run scripts/generate_image.py "make the background blue" --model flash --input /tmp/original.png

# Aspect ratio (solo imagen)
uv run scripts/generate_image.py "wide banner" --model imagen --aspect 16:9

# Output personalizado
uv run scripts/generate_image.py "icon" -o /tmp/icon.png
```

| Modelo | Alias | Costo | Mejor para |
|--------|-------|-------|-----------|
| Imagen 4.0 | `imagen` (default) | $0.040/img (free tier limitado) | Fotorrealismo, diversidad cultural |
| Gemini 2.5 Flash Image | `flash` | ~$0.039/img (token-based, free 500/dia) | Edicion, conversacional, rapido |
| Gemini 3 Pro Image | `pro` | Token-based | Mayor calidad |
| Gemini 3.1 Flash Image | `banana2` | Token-based | Ultimo modelo flash |

### fal_handler.py — Image

Genera imagenes via fal.ai. Acceso a FLUX, Ideogram, Recraft.

```bash
# FLUX Schnell — mas barato ($0.003/img), ~2s
uv run scripts/fal_handler.py image "sunset over patagonian mountains" --model schnell

# FLUX 1.1 Pro — mejor calidad mid-tier ($0.04/img)
uv run scripts/fal_handler.py image "professional headshot" --model flux-pro

# FLUX 1.1 Pro Ultra — maxima calidad FLUX ($0.06/img)
uv run scripts/fal_handler.py image "cinematic landscape 4K" --model flux-ultra

# Ideogram v2 — mejor texto en imagenes ($0.03/img, 98% precision)
uv run scripts/fal_handler.py image "poster that says SKYWALKING in bold" --model ideogram

# Recraft v3 — genera SVG/vectores ($0.04 raster, $0.08 SVG)
uv run scripts/fal_handler.py image "minimalist tech company logo" --model recraft

# Opciones
uv run scripts/fal_handler.py image "prompt" --size square_hd --num 2 --style realistic_image
```

| Modelo | Alias | Costo/img | Velocidad | Mejor para |
|--------|-------|-----------|-----------|-----------|
| FLUX.1 Schnell | `schnell` | $0.003 | ~2s (sync) | Prototyping, volumen, rapido |
| FLUX 1.1 Pro | `flux-pro` | $0.040 | ~8s (queue) | Produccion, calidad |
| FLUX 1.1 Pro Ultra | `flux-ultra` | $0.060 | ~12s (queue) | Maxima calidad, 2K |
| Ideogram v2 | `ideogram` | $0.030 | ~8s (queue) | Texto en imagenes, logos, social media |
| Recraft v3 | `recraft` | $0.040/$0.080 | ~8s (queue) | SVG/vectores, design assets, brand kits |

**Sizes disponibles:** `square_hd`, `square`, `portrait_4_3`, `portrait_16_9`, `landscape_4_3`, `landscape_16_9`

---

## Video Generation

### fal_handler.py — Video

Genera video via fal.ai. Async (queue + polling, 30-120s tipico).

```bash
# Wan 2.7 — default, open-source, buena calidad (~$0.05/sec)
uv run scripts/fal_handler.py video "drone shot over a mountain lake at sunrise" --model wan

# Wan 2.7 — mayor duracion
uv run scripts/fal_handler.py video "timelapse of clouds" --model wan --duration 10

# Veo 3.1 Lite — Google, mejor calidad/precio ($0.05/sec)
uv run scripts/fal_handler.py video "cinematic establishing shot of a city" --model veo

# Veo 3.1 Fast — con audio ($0.10/sec)
uv run scripts/fal_handler.py video "waves crashing on a beach" --model veo-fast

# Veo 3.1 Standard — maxima calidad, 4K + audio ($0.40/sec)
uv run scripts/fal_handler.py video "epic sunset timelapse" --model veo-std

# Kling 2.5 — mejor movimiento humano ($0.07/sec via fal.ai)
uv run scripts/fal_handler.py video "person walking through a forest" --model kling

# Sora 2 — OpenAI, clips largos hasta 20s ($0.10/sec)
uv run scripts/fal_handler.py video "a cat playing with yarn" --model sora

# PixVerse v6
uv run scripts/fal_handler.py video "abstract fluid motion" --model pixverse

# Aspect ratio
uv run scripts/fal_handler.py video "vertical story" --model wan --aspect 9:16
```

| Modelo | Alias | Costo/sec | Max dur | Res | Audio | Mejor para |
|--------|-------|-----------|---------|-----|-------|-----------|
| Wan 2.7 | `wan` (default) | ~$0.05 | 15s | 1080p | No | Default, open-source, buen balance |
| Wan 2.7 I2V | `wan-i2v` | ~$0.05 | 15s | 1080p | No | Animar una imagen existente |
| Veo 3.1 Lite | `veo` | $0.05 | 8s | 720p | No | Cheapest quality API |
| Veo 3.1 Fast | `veo-fast` | $0.10 | 8s | 720p | Si | Calidad + audio |
| Veo 3.1 Standard | `veo-std` | $0.40 | 8s | 4K | Si | Mejor cinematica, produccion |
| Kling 2.5 Pro | `kling` | $0.07 | 10s | 1080p | No | Mejor movimiento humano |
| Kling 2.5 I2V | `kling-i2v` | $0.07 | 10s | 1080p | No | Animar imagen con Kling |
| Kling 3.0 I2V | `kling3` | ~$0.15 | 10s | 1080p | No | Ultima version Kling |
| Sora 2 | `sora` | $0.10 | 20s | 720p | No | Clips mas largos (20s) |
| PixVerse v6 | `pixverse` | ~$0.08 | 8s | 1080p | No | Efectos estilizados |

**Duration:** entero (2-15 para wan, 5-20 para sora, 5-8 para veo)
**Aspect ratios:** `16:9`, `9:16`, `1:1`

---

## Router shortcuts

```bash
# Via router — usa el modelo optimo automaticamente
bash scripts/router.sh image "a sunset"           # → FLUX Schnell
bash scripts/router.sh image-pro "product shot"    # → FLUX 1.1 Pro
bash scripts/router.sh image-text "poster text"    # → Ideogram v2
bash scripts/router.sh image-svg "logo design"     # → Recraft v3
bash scripts/router.sh video "drone shot"          # → Wan 2.7
bash scripts/router.sh video-pro "cinematic"       # → Veo 3.1 Lite
bash scripts/router.sh video-cinema "epic scene"   # → Veo 3.1 Standard
```

---

## Cuando usar cada handler

| Necesidad | Handler | Modelo |
|-----------|---------|--------|
| Imagen rapida/gratis | `generate_image.py` | flash (free 500/dia) |
| Imagen + edicion conversacional | `generate_image.py` | flash (soporta --input) |
| Imagen fotorrealista premium | `generate_image.py` | imagen |
| Imagen volumen barato | `fal_handler.py` | schnell ($0.003) |
| Texto legible en imagen | `fal_handler.py` | ideogram (98% precision) |
| SVG / vectores / logos | `fal_handler.py` | recraft |
| Imagen maxima calidad | `fal_handler.py` | flux-ultra |
| Video default | `fal_handler.py` | wan |
| Video cheapest quality | `fal_handler.py` | veo ($0.05/sec) |
| Video + audio nativo | `fal_handler.py` | veo-fast o veo-std |
| Video 4K cinematico | `fal_handler.py` | veo-std ($0.40/sec) |
| Video movimiento humano | `fal_handler.py` | kling |
| Video largo (20s) | `fal_handler.py` | sora |
| Animar imagen estatica | `fal_handler.py` | wan-i2v o kling-i2v |

---

## Env vars necesarias

```bash
# En hive/.env
GEMINI_API_KEY=xxx    # generate_image.py (Imagen 4.0, Flash)
FAL_KEY=xxx           # fal_handler.py (FLUX, Kling, Veo, Sora, etc)
```

API keys:
- Gemini: https://aistudio.google.com/apikey (free)
- fal.ai: https://fal.ai/dashboard/keys ($5 free credit)
