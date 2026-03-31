#!/usr/bin/env python3
"""Hive Monitor — poll GitHub/npm for Claude Code ecosystem updates, notify #hive in Slack.

Runs hourly via GitHub Actions. Checks for new releases in the last 75 minutes.
For each update, posts a rich Slack message with: what changed, link, and how it helps us.
"""

# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

import json
import urllib.request
import urllib.error
import os
import sys
from datetime import datetime, timezone, timedelta

POLL_INTERVAL_MINUTES = 75  # cron every 60min + 15min buffer
SLACK_CHANNEL = "C0APTL4JLCE"  # #hive

GITHUB_SOURCES = [
    {
        "name": "Claude Code",
        "repo": "anthropics/claude-code",
        "context": "Nuestro IDE principal. Mejoras impactan velocidad de desarrollo, calidad de agents, y capabilities de Mentat.",
    },
    {
        "name": "Claude Code Action",
        "repo": "anthropics/claude-code-action",
        "context": "Automatización CI/CD con Claude. Mejoras impactan PR reviews, issue triage, y workflows de GitHub.",
    },
    {
        "name": "Claude Code Skills",
        "repo": "anthropics/skills",
        "context": "Skills oficiales de Anthropic. Nuevos skills pueden reemplazar o mejorar los nuestros en Hive.",
    },
]

NPM_PACKAGES = [
    {
        "name": "Claude Code (npm)",
        "package": "@anthropic-ai/claude-code",
        "context": "SDK programático de Claude Code. Mejoras habilitan nuevas integraciones y automatizaciones.",
    },
    {
        "name": "Claude Agent SDK",
        "package": "@anthropic-ai/claude-agent-sdk",
        "context": "SDK para construir agents. Core de Micelio — mejoras directamente aplican a nuestro producto.",
    },
]

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")


def _github_headers():
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "hive-monitor/1.0",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def check_github_release(source: dict) -> dict | None:
    url = f"https://api.github.com/repos/{source['repo']}/releases/latest"
    req = urllib.request.Request(url, headers=_github_headers())

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise

    published = datetime.fromisoformat(data["published_at"].replace("Z", "+00:00"))
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=POLL_INTERVAL_MINUTES)

    if published > cutoff:
        body = data.get("body", "") or ""
        return {
            "source": "github",
            "name": source["name"],
            "repo": source["repo"],
            "version": data["tag_name"],
            "url": data["html_url"],
            "body": body,
            "published": data["published_at"],
            "context": source["context"],
        }
    return None


def check_npm_package(source: dict) -> dict | None:
    pkg = source["package"].replace("/", "%2F")
    url = f"https://registry.npmjs.org/{pkg}/latest"
    req = urllib.request.Request(url, headers={"User-Agent": "hive-monitor/1.0"})

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError:
        return None

    version = data.get("version", "unknown")
    full_url = f"https://registry.npmjs.org/{pkg}"
    req2 = urllib.request.Request(full_url, headers={"User-Agent": "hive-monitor/1.0"})

    try:
        with urllib.request.urlopen(req2, timeout=10) as resp2:
            full_data = json.loads(resp2.read())
        time_info = full_data.get("time", {})
        published_str = time_info.get(version)
        if not published_str:
            return None
        published = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
    except Exception:
        return None

    cutoff = datetime.now(timezone.utc) - timedelta(minutes=POLL_INTERVAL_MINUTES)

    if published > cutoff:
        return {
            "source": "npm",
            "name": source["name"],
            "package": source["package"],
            "version": version,
            "url": f"https://www.npmjs.com/package/{source['package']}",
            "body": "",
            "published": published_str,
            "context": source["context"],
        }
    return None


def _summarize_release(body: str, max_lines: int = 8) -> str:
    """Extract key changes from release notes markdown."""
    if not body:
        return "_Sin release notes disponibles._"

    lines = []
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        # skip markdown headers, HR, images, links-only lines
        if stripped.startswith(("![", "---", "***", "<")):
            continue
        lines.append(stripped)
        if len(lines) >= max_lines:
            break

    return "\n".join(lines) if lines else "_Sin release notes disponibles._"


def notify_slack(updates: list[dict]):
    if not SLACK_BOT_TOKEN or not updates:
        return False

    for u in updates:
        icon = ":github:" if u["source"] == "github" else ":package:"
        summary = _summarize_release(u["body"])

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{u['name']} → {u['version']}",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{icon} *<{u['url']}|Ver release>*",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Cambios:*\n{summary}",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Impacto Skywalking:*\n{u['context']}",
                },
            },
            {"type": "divider"},
        ]

        payload = {
            "channel": SLACK_CHANNEL,
            "text": f"{u['name']} {u['version']} — nueva release",
            "blocks": blocks,
        }

        req = urllib.request.Request(
            "https://slack.com/api/chat.postMessage",
            data=json.dumps(payload).encode(),
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            if not result.get("ok"):
                print(f"Slack error for {u['name']}: {result.get('error')}", file=sys.stderr)

    return True


def main():
    updates = []
    errors = []

    for source in GITHUB_SOURCES:
        try:
            result = check_github_release(source)
            if result:
                updates.append(result)
        except Exception as e:
            errors.append(f"github/{source['repo']}: {e}")

    for source in NPM_PACKAGES:
        try:
            result = check_npm_package(source)
            if result:
                updates.append(result)
        except Exception as e:
            errors.append(f"npm/{source['package']}: {e}")

    print(f"Checked {len(GITHUB_SOURCES) + len(NPM_PACKAGES)} sources, {len(updates)} updates found")

    if errors:
        for e in errors:
            print(f"  ERROR: {e}", file=sys.stderr)

    # Set GitHub Actions outputs
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        slim = [
            {"name": u["name"], "version": u["version"], "url": u["url"],
             "source": u["source"], "context": u["context"]}
            for u in updates
        ]
        with open(github_output, "a") as f:
            f.write(f"has_updates={'true' if updates else 'false'}\n")
            # Use delimiter for multiline JSON
            f.write("updates_json<<EOJSON\n")
            f.write(json.dumps(slim))
            f.write("\nEOJSON\n")

    if updates:
        for u in updates:
            print(f"  {u['name']} → {u['version']}")
    else:
        print("  No new updates")


if __name__ == "__main__":
    main()
