---
name: perplexity
description: Search the web and query LLMs with real-time data via Perplexity API. Use when user needs web research, current information, grounded answers with citations, or wants to search using Perplexity's Sonar models. Triggers on web search, research queries, "ask perplexity", current events, or real-time data needs.
allowed-tools: Bash, Read
---

# Perplexity API

Web search + grounded LLM responses via bash/curl. Three APIs: Sonar (chat+search), Search (raw results), Agent (multi-provider).

## Prerequisites
- `PERPLEXITY_API_KEY` in `.env`
- `jq` installed

## Quick Commands

```bash
# Ask a question (Sonar - default, includes citations)
hive/scripts/perplexity_handler.sh ask "What are the latest developments in AI?"

# Ask with specific model
hive/scripts/perplexity_handler.sh ask "Explain quantum computing" --model sonar-pro

# Search only (raw web results, no LLM summary)
hive/scripts/perplexity_handler.sh search "best python web frameworks 2026"

# Search with filters
hive/scripts/perplexity_handler.sh search "machine learning papers" --domains arxiv.org,scholar.google.com --max-results 5

# Agent API (use third-party models with web search)
hive/scripts/perplexity_handler.sh agent "Compare GPT-5 vs Claude Opus" --model openai/gpt-5.2

# Streaming response
hive/scripts/perplexity_handler.sh ask "Summarize today's tech news" --stream
```

## APIs

### Sonar (default) - `/chat/completions`
Best for: Q&A with web-grounded citations. OpenAI-compatible format.

```bash
# Basic
hive/scripts/perplexity_handler.sh ask "query"

# With filters
hive/scripts/perplexity_handler.sh ask "query" --domains example.com --recency month

# Structured JSON output
hive/scripts/perplexity_handler.sh ask "Top 3 AI startups with funding" --json-schema '{"type":"object","properties":{"startups":{"type":"array","items":{"type":"object","properties":{"name":{"type":"string"},"funding":{"type":"string"},"focus":{"type":"string"}},"required":["name","funding","focus"]}}},"required":["startups"]}'

# With system prompt
hive/scripts/perplexity_handler.sh ask "query" --system "You are a research assistant. Be precise and cite sources."
```

**Models:** `sonar` (fast), `sonar-pro` (thorough), `sonar-reasoning` (step-by-step), `sonar-reasoning-pro` (deep reasoning)

### Search - `/search`
Best for: Raw ranked web results without LLM processing.

```bash
hive/scripts/perplexity_handler.sh search "query" [options]
  --max-results 10          # 1-20, default 10
  --domains arxiv.org       # comma-separated allowlist
  --exclude-domains spam.com # comma-separated denylist (cannot mix with --domains)
  --country US              # ISO 3166-1 alpha-2
  --language en,es          # ISO 639-1 codes
```

### Agent - `/v1/responses`
Best for: Multi-provider models (OpenAI, Anthropic, Google) with web search tool.

```bash
hive/scripts/perplexity_handler.sh agent "query" [options]
  --model openai/gpt-5.2    # or any supported provider/model
  --tools web_search         # default; also: fetch_url
  --max-tokens 1000
  --reasoning high           # effort level for reasoning models
  --stream
```

## Recency Filter Values
`hour` `day` `week` `month`

## Output Format

```json
{
  "success": true,
  "data": { ... }
}
```

Sonar responses include `citations` array with source URLs when available.

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| 401 | Invalid API key | Check PERPLEXITY_API_KEY in .env |
| 429 | Rate limited | Wait and retry |
| 400 | Invalid params | Check model name, filters |
