---
name: generate_audio
description: Generate speech via OpenAI TTS — Mentat's voice. Use when user wants to hear a response spoken, generate audio briefings, or create voice content. Supports ES-LATAM and EN-UK.
allowed-tools: Bash(uv run:*), Bash(OPENAI_API_KEY=*), Bash(afplay:*), Read
---

# Generate Audio (Speak)

Mentat's voice — text to speech via OpenAI TTS API.

## When to Use

- User says "dime", "habla", "speak", "read this aloud", or any request to hear rather than read
- Generating audio briefings, summaries, or narrations
- User explicitly asks for voice/audio output

## Mentat Voice Identity

| Attribute | Value |
|-----------|-------|
| Voice | `onyx` — deep, calm, authoritative |
| Model | `gpt-4o-mini-tts` (best Spanish pronunciation + style control) |
| Speed | 1.15 (slightly faster than default) |
| ES style | ES-LATAM neutro, ritmo firme, sin afectación |
| EN style | British English, measured cadence |

**Default instructions (baked into Mentat's character):**
```
Speak in clear Latin American Spanish. Tone: serious but warm, like a trusted strategic advisor. Cadence: deliberate, slightly faster than normal. Emotion: confident and grounded. Accent: neutral Latin American, no Spain. Style: like a senior consultant giving a private briefing.
```

For English, swap to:
```
Speak in British English. Tone: serious but warm, like a trusted strategic advisor. Cadence: deliberate, slightly faster than normal. Emotion: confident and grounded. Style: like a senior consultant giving a private briefing.
```

The voice is consistent across languages. Mentat sounds the same whether speaking Spanish or English — only the language changes, not the character.

## Usage

```bash
# Basic — speak in Spanish (default)
uv run scripts/generate_audio.py "Análisis completado. Tres puntos clave."

# English
uv run scripts/generate_audio.py "Analysis complete. Three key points." --lang en

# From file
uv run scripts/generate_audio.py --file /tmp/briefing.txt -o /tmp/briefing.mp3

# From stdin (pipe content)
echo "Quick status update" | uv run scripts/generate_audio.py --stdin --lang en

# Custom output path
uv run scripts/generate_audio.py "Hola" -o /tmp/greeting.mp3

# Expressive model with style instructions
uv run scripts/generate_audio.py "Breaking news." -m gpt-4o-mini-tts --instructions "Speak slowly and deliberately, like a trusted advisor"

# Generate comparison samples (all voices)
uv run scripts/generate_audio.py --samples
uv run scripts/generate_audio.py --samples "Custom sample text here"

# Don't auto-play
uv run scripts/generate_audio.py "Silent generation" --no-play
```

## Handler

`scripts/generate_audio.py` — standalone Python script, only needs `requests`.

## Models

| Model | Flag | Best For | Cost |
|-------|------|----------|------|
| tts-1-hd | `-m tts-1-hd` (default) | Quality output, briefings | $30/1M chars |
| tts-1 | `-m tts-1` | Fast drafts, iteration | $15/1M chars |
| gpt-4o-mini-tts | `-m gpt-4o-mini-tts` | Expressive, style control | $12/1M chars |

## Voices (Reference)

| Voice | Character | Mentat fit |
|-------|-----------|------------|
| **onyx** | Deep, authoritative | **Default** — matches Mentat's analytical directness |
| echo | Clear, direct | Backup — slightly lighter |
| fable | Warm, British-leaning | Good for EN-UK content |
| ash | Warm, conversational | Too casual |
| coral | Warm, friendly | Too soft |
| nova | Energetic | Too bright |
| sage | Wise, calm | Alternative if onyx is too heavy |
| shimmer | Bright, optimistic | Doesn't fit |
| alloy | Neutral, balanced | Generic |
| ballad | Storytelling | Too performative |

## Rules

- Always run from `hive/` directory
- Default output: `/tmp/mentat_speech.mp3`
- **Auto-plays on macOS** after generating (use `--no-play` to suppress)
- Max 4096 chars per request (API limit) — longer texts get truncated with warning
- For long content, split into logical chunks and generate separately
- Voice selection is an identity decision — don't change without user request

## Workflow: Spoken Response

```
1. Prepare text (clean markdown, remove code blocks, keep prose)
2. Detect language (default ES, switch to EN if content is English)
3. Generate with Mentat's voice
4. Auto-play
5. Save path for reference
```

## Anti-patterns

| Don't | Why | Do Instead |
|-------|-----|------------|
| Read raw markdown aloud | Sounds robotic with headers/bullets | Convert to natural prose first |
| Switch voices mid-session | Breaks identity consistency | Always use Mentat's voice unless sampling |
| Generate > 4096 chars | API truncates silently | Split into chunks |
| Use tts-1 for final output | Audibly lower quality | Use tts-1-hd (default) |
