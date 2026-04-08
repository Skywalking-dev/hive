---
name: llm-landscape
description: Research and update the LLM API Landscape document with current pricing, providers, free tiers, and recommendations.
triggers:
  - "llm landscape"
  - "llm pricing"
  - "update llm"
  - "api pricing"
  - "model pricing"
  - "llm costs"
---

# LLM API Landscape Update

Research the current LLM API ecosystem and update `docs/LLM_API_LANDSCAPE.md` with accurate, comprehensive data.

## Execution

### Step 1: Research (parallel Oraculo agents)

Launch **three** Oraculo research agents in parallel:

**Agent A — Frontier & paid providers:**
```
Research ALL current LLM API providers with public pricing as of today.
For each provider: model names, input/output $/MTok, cached pricing, context window, free tier, OAI-compatibility.
Providers to cover: Anthropic, OpenAI, Google, xAI/Grok, DeepSeek, Mistral, Alibaba/Qwen, Baidu/ERNIE, Zhipu AI, Moonshot/Kimi, Cohere, Perplexity, AI21/Jamba, Reka, Meta/Llama hosted options.
Also check: Fireworks AI, SambaNova, Hyperbolic, DeepInfra, Novita AI, Together AI, Amazon Bedrock, Azure OpenAI.
Flag any new providers not in the current doc.
Flag any pricing changes in the last 30 days.
Flag any deprecated or removed models.
```

**Agent B — Free tiers & inference hosts:**
```
Research ALL free-tier and ultra-low-cost LLM inference providers available today.
For each: exact rate limits (RPM, RPD, TPD, TPM), which models are free, permanent vs trial, OAI-compat, tool use, vision, speed.
Cover: Groq, Cerebras, SambaNova, Google Gemini, OpenRouter, SiliconFlow, Cloudflare Workers AI, Together AI, Mistral, Cohere, NVIDIA NIM, HuggingFace, Fireworks, Hyperbolic.
Assess production reliability of each free tier.
Note any recently removed or reduced free tiers.
```

**Agent C — Image & video generation APIs:**
```
Research ALL image and video generation API providers with public pricing.
IMAGE: OpenAI gpt-image-1/DALL-E, Google Imagen 4/Gemini native, BFL FLUX (all variants), Stability AI, Ideogram, Recraft, Leonardo, Replicate, fal.ai, Fireworks, Hyperbolic, Cloudflare Workers AI, Bedrock Titan, Azure DALL-E.
VIDEO: Google Veo 3.x, OpenAI Sora 2, Runway Gen-4, Kling, Pika, Luma, Minimax/Hailuo, ByteDance/Seedance, Wan2.x, CogVideoX, Hunyuan, Bedrock Nova Reel.
For images: price/image, resolution, free tier, key strength, text rendering quality, SVG support.
For video: price/second, max duration, resolution, API availability, free tier.
Note dead ends: Midjourney (no API), Meta Movie Gen (no API), Stability Video (deprecated).
```

### Step 2: Update document

Read `docs/LLM_API_LANDSCAPE.md` and update ALL sections:

1. **Header stats** — Update provider count, free tier count, country count, max savings %, cheapest $/MTok
2. **Key Takeaways & Recommendations** — Rewrite based on current data. Include:
   - Market snapshot (3-4 bullets on trends)
   - Recommendations for Skywalking/Hive (numbered, actionable)
   - Trends to watch (3-4 bullets)
3. **Section 1: Frontier Models** — Update pricing tables (US, CN, EU, Other). Add new providers, remove deprecated models, mark legacy with ~~strikethrough~~
4. **Section 2: Inference Hosting** — Update aggregator table
5. **Section 3: Free Tier Providers** — Update limits, models, production suitability. Update recommended free stack
6. **Section 4: Cost ranking** — Rebuild sorted table from all providers
7. **Section 5: Use Case Routing** — Update best picks based on new pricing
8. **Section 6: Integration Priority** — Mark completed handlers, reprioritize pending based on ROI
9. **Section 7: Batch discounts** — Update
10. **Section 8: Savings scenarios** — Recalculate with current prices
11. **Section 9: Recent changes** — Replace with last 30 days of changes
12. **Section 10: Dead ends** — Update non-viable providers
13. **Section 11: Image Generation** — Update pricing table sorted by $/image. Include free tiers (Cloudflare, Gemini). Cover: OpenAI gpt-image-1, Gemini/Imagen, FLUX (BFL/Replicate/fal.ai/Fireworks), Stability AI, Ideogram, Recraft, Hyperbolic, Leonardo, Bedrock Titan. Add best-pick-by-use-case table.
14. **Section 12: Video Generation** — Update pricing table sorted by $/sec. Cover: Veo 3.x, Sora 2, Runway Gen-4, Kling, Pika, Luma, Minimax/Hailuo, ByteDance/Seedance, Wan2.x (open-source), CogVideoX, Hunyuan, Bedrock Nova Reel. Add best-pick-by-use-case table. Note dead ends (Midjourney no API, Meta no API, Stability video deprecated).

### Step 3: Cross-reference with Hive handlers

Check which providers in `hive/scripts/` already have handlers integrated:
```bash
ls /Users/gpublica/workspace/skywalking/hive/scripts/*_handler.*
```

Update Section 6 integration priority to reflect current handler status (Done vs Pending).

### Step 4: Update date

Change the "Last updated" date in the document header to today's date.

## Rules

- All prices in USD per million tokens ($/MTok)
- Use `**bold**` for best-in-class values
- Use `~~strikethrough~~` for deprecated/legacy models
- Sort cost ranking table ascending by output price
- Mark free tiers clearly: permanent vs trial credits vs rate-limited
- Include OAI-compatibility status for every provider (critical for Hive integration)
- Flag low-confidence pricing with a note
- Do NOT remove providers from the doc — mark dead ones in Section 10
- Keep format consistent with existing document structure

## Scheduling

This skill can be run manually (`/llm-landscape`) or scheduled via cron.
Recommended frequency: **monthly** (first week of each month).
Pricing changes are infrequent enough that monthly is sufficient; flag breaking changes ad-hoc.
