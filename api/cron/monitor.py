"""Hive Monitor — poll GitHub/npm for Claude Code ecosystem updates, notify Slack."""

from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import urllib.error
import os
from datetime import datetime, timezone, timedelta

POLL_INTERVAL_MINUTES = 75  # cron every 60min + 15min buffer

GITHUB_SOURCES = [
    {"name": "Claude Code", "repo": "anthropics/claude-code"},
    {"name": "Claude Code Action", "repo": "anthropics/claude-code-action"},
    {"name": "Claude Code Skills", "repo": "anthropics/skills"},
]

NPM_PACKAGES = [
    {"name": "Claude Code (npm)", "package": "@anthropic-ai/claude-code"},
    {"name": "Claude Agent SDK", "package": "@anthropic-ai/claude-agent-sdk"},
]

SLACK_WEBHOOK = os.environ.get("SLACK_WEBHOOK_URL")


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
            "summary": body[:400],
            "published": data["published_at"],
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

    # npm doesn't expose publish time in /latest — fetch from full package metadata
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
            "summary": "",
            "published": published_str,
        }
    return None


def notify_slack(updates: list[dict]):
    if not SLACK_WEBHOOK or not updates:
        return False

    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "Hive Monitor — New Updates"},
        }
    ]

    for u in updates:
        icon = ":github:" if u["source"] == "github" else ":npm:"
        text = f"{icon} *{u['name']}* → `{u['version']}`\n<{u['url']}>"
        if u.get("summary"):
            text += f"\n\n{u['summary'][:300]}"

        blocks.append(
            {"type": "section", "text": {"type": "mrkdwn", "text": text}}
        )

    payload = {
        "text": f"{len(updates)} update(s) detected in Claude Code ecosystem",
        "blocks": blocks,
    }

    req = urllib.request.Request(
        SLACK_WEBHOOK,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    urllib.request.urlopen(req, timeout=10)
    return True


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
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

        notified = notify_slack(updates) if updates else False

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(
            json.dumps(
                {
                    "checked": len(GITHUB_SOURCES) + len(NPM_PACKAGES),
                    "updates": len(updates),
                    "notified": notified,
                    "details": updates,
                    "errors": errors,
                }
            ).encode()
        )
