#!/usr/bin/env python3
"""
Hive Release Script
Installs hive skills, agents, and configs into the parent workspace.

Creates symlinks so that opening Claude Code (or Cursor, Gemini CLI, Codex)
from the workspace root gives access to all hive skills and agents.

Structure after release:
  skywalking/                    ← workspace root
  ├── .claude/
  │   ├── skills/ → hive/skills/
  │   └── agents/ → hive/agents/
  ├── .cursor/rules/             ← generated .mdc files
  ├── .mcp.json                  ← merged MCP configs
  └── hive/                      ← this repo (source of truth)
"""

import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

# Directories
HIVE_DIR = Path(__file__).parent.resolve()
WORKSPACE_ROOT = HIVE_DIR.parent
SKILLS_DIR = HIVE_DIR / "skills"
AGENTS_DIR = HIVE_DIR / "agents"


def info(msg: str):
    print(f"[hive] {msg}")


def warn(msg: str):
    print(f"[hive] WARN: {msg}", file=sys.stderr)


def backup_path(path: Path) -> Path:
    """Create timestamped backup of existing path."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup = path.with_suffix(f".backup.{timestamp}{path.suffix}")
    shutil.move(str(path), str(backup))
    info(f"Backed up {path.name} -> {backup.name}")
    return backup


def create_symlink(target: Path, link_path: Path, label: str):
    """Create or update symlink."""
    link_path.parent.mkdir(parents=True, exist_ok=True)

    if link_path.is_symlink():
        current = link_path.resolve()
        if current == target.resolve():
            info(f"{label}: already linked")
            return
        backup_path(link_path)
    elif link_path.exists():
        backup_path(link_path)

    link_path.symlink_to(target)
    info(f"{label}: linked -> {target}")


def build_cursor_rules(skills_dir: Path, rules_dir: Path):
    """Generate .mdc files from skills for Cursor."""
    rules_dir.mkdir(parents=True, exist_ok=True)

    for mdc in rules_dir.glob("*.mdc"):
        mdc.unlink()

    count = 0
    for skill_path in skills_dir.iterdir():
        if not skill_path.is_dir():
            continue

        skill_md = skill_path / "SKILL.md"
        if not skill_md.exists():
            skill_md = skill_path / "skill.md"
        if not skill_md.exists():
            continue

        out_file = rules_dir / f"{skill_path.name}.mdc"
        shutil.copy(skill_md, out_file)
        count += 1

    info(f"Cursor rules: {count} skills → .mdc files")


def merge_mcp_configs(source: Path, target: Path):
    """Merge MCP servers from source into target."""
    if not source.exists():
        return

    if target.exists():
        with open(target) as f:
            target_cfg = json.load(f)
    else:
        target_cfg = {"mcpServers": {}}

    with open(source) as f:
        source_cfg = json.load(f)

    source_servers = source_cfg.get("mcpServers", {})
    target_servers = target_cfg.setdefault("mcpServers", {})

    added = []
    for name, server in source_servers.items():
        if name not in target_servers:
            target_servers[name] = server
            added.append(name)

    if added:
        with open(target, "w") as f:
            json.dump(target_cfg, f, indent=2)
            f.write("\n")
        info(f"MCP servers added: {', '.join(added)}")
    else:
        info("MCP servers: all already present")


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Install hive skills and agents into workspace"
    )
    parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation")
    args = parser.parse_args()

    info(f"Hive: {HIVE_DIR}")
    info(f"Workspace: {WORKSPACE_ROOT}")

    if not SKILLS_DIR.exists():
        warn(f"Skills not found: {SKILLS_DIR}")
        return 1

    # Show plan
    info("Actions:")
    print(f"  Symlink {WORKSPACE_ROOT}/.claude/skills → {SKILLS_DIR}")
    print(f"  Symlink {WORKSPACE_ROOT}/.claude/agents → {AGENTS_DIR}")
    print(f"  Generate .cursor/rules/ from skills")
    print(f"  Merge .mcp.json configs")
    print()

    if not args.yes:
        if not sys.stdin.isatty():
            warn("No TTY; use --yes to skip confirmation")
            return 1
        reply = input("[hive] Proceed? [y/N]: ").strip().lower()
        if reply not in ("y", "yes"):
            info("Cancelled")
            return 1

    # 1. Claude Code — symlink skills + agents to workspace
    create_symlink(SKILLS_DIR, WORKSPACE_ROOT / ".claude" / "skills", "Claude skills")
    create_symlink(AGENTS_DIR, WORKSPACE_ROOT / ".claude" / "agents", "Claude agents")

    # 2. Cursor — generate .mdc rules
    cursor_rules = WORKSPACE_ROOT / ".cursor" / "rules"
    build_cursor_rules(SKILLS_DIR, cursor_rules)

    # 3. MCP configs — merge hive's into workspace
    hive_mcp = HIVE_DIR / ".mcp.json"
    workspace_mcp = WORKSPACE_ROOT / ".mcp.json"
    if hive_mcp.exists():
        merge_mcp_configs(hive_mcp, workspace_mcp)

    info("Done. Open Claude Code from workspace root to use hive skills.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
