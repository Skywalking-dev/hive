#!/usr/bin/env python3
"""Hive Monitor — poll GitHub/npm for Claude Code ecosystem updates.

Runs every 6h via GitHub Actions. Checks for new releases within the poll window.
Outputs updates_json for the maintain job, which handles Slack notification.
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

POLL_INTERVAL_MINUTES = 375  # cron every 6h + 15min buffer

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
