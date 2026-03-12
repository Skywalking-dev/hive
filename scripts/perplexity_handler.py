#!/usr/bin/env python3
"""
Perplexity API handler for Hive.
Sonar (chat+search), Search (raw results), Agent (multi-provider).
"""

import os
import sys
import json
import argparse
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError


# --- Config ---

BASE_URL = "https://api.perplexity.ai"


def get_api_key() -> str:
    key = os.environ.get("PERPLEXITY_API_KEY")
    if not key:
        raise ValueError("PERPLEXITY_API_KEY not set in environment")
    return key


# --- Core API ---

def api_call(endpoint: str, payload: dict, stream: bool = False) -> dict | str:
    """POST request to Perplexity API."""
    url = f"{BASE_URL}{endpoint}"
    data = json.dumps(payload).encode()
    req = Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {get_api_key()}")
    req.add_header("Content-Type", "application/json")

    try:
        resp = urlopen(req, timeout=120)
        if stream:
            output = []
            for line in resp:
                line = line.decode().strip()
                if line.startswith("data: "):
                    chunk = line[6:]
                    if chunk == "[DONE]":
                        break
                    try:
                        data = json.loads(chunk)
                        delta = data.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            output.append(content)
                            print(content, end="", flush=True)
                    except json.JSONDecodeError:
                        pass
            print()
            return "".join(output)
        return json.loads(resp.read())
    except HTTPError as e:
        body = e.read().decode() if e.fp else ""
        try:
            err = json.loads(body)
        except Exception:
            err = {"raw": body}
        return {"error": True, "status": e.code, "detail": err}


# --- Commands ---

def cmd_ask(args):
    """Sonar chat completion with web search."""
    messages = []
    if args.system:
        messages.append({"role": "system", "content": args.system})
    messages.append({"role": "user", "content": args.query})

    payload = {
        "model": args.model,
        "messages": messages,
    }

    if args.stream:
        payload["stream"] = True

    # Web search options
    web_opts = {}
    if args.domains:
        web_opts["search_domain_filter"] = args.domains.split(",")
    if args.recency:
        web_opts["search_recency_filter"] = args.recency
    if web_opts:
        payload["web_search_options"] = web_opts

    # Structured output
    if args.json_schema:
        try:
            schema = json.loads(args.json_schema)
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {"schema": schema},
            }
        except json.JSONDecodeError:
            return output(False, error="Invalid JSON schema")

    if args.stream:
        content = api_call("/chat/completions", payload, stream=True)
        if isinstance(content, dict) and content.get("error"):
            return output(False, error=content)
        return output(True, data={"content": content, "model": args.model})

    result = api_call("/chat/completions", payload)
    if isinstance(result, dict) and result.get("error"):
        return output(False, error=result)

    choice = result.get("choices", [{}])[0]
    data = {
        "content": choice.get("message", {}).get("content", ""),
        "model": result.get("model", args.model),
        "usage": result.get("usage", {}),
    }
    # Extract citations if present
    citations = result.get("citations")
    if citations:
        data["citations"] = citations

    return output(True, data=data)


def cmd_search(args):
    """Raw web search results."""
    payload = {"query": args.query}

    if args.max_results:
        payload["max_results"] = args.max_results
    if args.domains:
        payload["search_domain_filter"] = args.domains.split(",")
    if args.exclude_domains:
        payload["search_domain_filter"] = [f"-{d}" for d in args.exclude_domains.split(",")]
    if args.country:
        payload["country"] = args.country
    if args.language:
        payload["search_language_filter"] = args.language.split(",")

    result = api_call("/search", payload)
    if isinstance(result, dict) and result.get("error"):
        return output(False, error=result)

    return output(True, data=result)


def cmd_agent(args):
    """Agent API - multi-provider with web search."""
    payload = {
        "model": args.model,
        "input": args.query,
    }

    if args.max_tokens:
        payload["max_output_tokens"] = args.max_tokens
    if args.stream:
        payload["stream"] = True

    # Tools
    if args.tools:
        payload["tools"] = [{"type": t} for t in args.tools.split(",")]
    else:
        payload["tools"] = [{"type": "web_search"}]

    # Reasoning
    if args.reasoning:
        payload["reasoning"] = {"effort": args.reasoning}

    if args.stream:
        # Agent streaming uses SSE format
        content = api_call("/v1/responses", payload, stream=True)
        if isinstance(content, dict) and content.get("error"):
            return output(False, error=content)
        return output(True, data={"content": content, "model": args.model})

    result = api_call("/v1/responses", payload)
    if isinstance(result, dict) and result.get("error"):
        return output(False, error=result)

    # Extract text from agent response
    out_text = ""
    for item in result.get("output", []):
        if item.get("type") == "message":
            for c in item.get("content", []):
                if c.get("type") == "output_text":
                    out_text += c.get("text", "")

    data = {
        "content": result.get("output_text", out_text),
        "model": result.get("model", args.model),
        "usage": result.get("usage", {}),
    }

    return output(True, data=data)


# --- Output ---

def output(success: bool, data: Optional[dict] = None, error=None):
    result = {"success": success}
    if data:
        result["data"] = data
    if error:
        result["error"] = error
    print(json.dumps(result, indent=2, ensure_ascii=False))


# --- CLI ---

def main():
    parser = argparse.ArgumentParser(description="Perplexity API handler")
    sub = parser.add_subparsers(dest="command", required=True)

    # ask (Sonar)
    ask_p = sub.add_parser("ask", help="Chat with Sonar (web-grounded)")
    ask_p.add_argument("query", help="Question to ask")
    ask_p.add_argument("--model", default="sonar-pro", help="Model: sonar, sonar-pro, sonar-reasoning, sonar-reasoning-pro")
    ask_p.add_argument("--system", help="System prompt")
    ask_p.add_argument("--domains", help="Comma-separated domain filter")
    ask_p.add_argument("--recency", choices=["hour", "day", "week", "month"], help="Recency filter")
    ask_p.add_argument("--json-schema", help="JSON schema for structured output")
    ask_p.add_argument("--stream", action="store_true", help="Stream response")

    # search
    search_p = sub.add_parser("search", help="Raw web search results")
    search_p.add_argument("query", help="Search query")
    search_p.add_argument("--max-results", type=int, default=10, help="Max results (1-20)")
    search_p.add_argument("--domains", help="Comma-separated domain allowlist")
    search_p.add_argument("--exclude-domains", help="Comma-separated domain denylist")
    search_p.add_argument("--country", help="ISO 3166-1 alpha-2 country code")
    search_p.add_argument("--language", help="Comma-separated ISO 639-1 language codes")

    # agent
    agent_p = sub.add_parser("agent", help="Agent API (multi-provider + web search)")
    agent_p.add_argument("query", help="Question to ask")
    agent_p.add_argument("--model", default="openai/gpt-5.2", help="Provider/model identifier")
    agent_p.add_argument("--tools", help="Comma-separated tools: web_search,fetch_url")
    agent_p.add_argument("--max-tokens", type=int, help="Max output tokens")
    agent_p.add_argument("--reasoning", choices=["low", "medium", "high"], help="Reasoning effort")
    agent_p.add_argument("--stream", action="store_true", help="Stream response")

    args = parser.parse_args()
    handlers = {"ask": cmd_ask, "search": cmd_search, "agent": cmd_agent}
    handlers[args.command](args)


if __name__ == "__main__":
    # Load .env if dotenv available
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    main()
