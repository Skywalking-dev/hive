#!/usr/bin/env python3
"""
Hive Release Script
Propagates .claude/ (source of truth) to all AI providers.

Equivalent to Formica's release_ants.sh but in Python.
"""

import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

# Directories
SCRIPT_DIR = Path(__file__).parent.resolve()
WORKSPACE_ROOT = SCRIPT_DIR.parent  # skywalking/
HIVE_DIR = SCRIPT_DIR

# Source of truth
CLAUDE_DIR = HIVE_DIR / ".claude"
SKILLS_DIR = CLAUDE_DIR / "skills"

# Target directories
# NOTE: commands removed — skills cover all use cases
TARGETS = {
    "workspace": {
        ".claude/skills": SKILLS_DIR,
        ".cursor/rules": None,  # Generated from skills
    },
    "hive": {
        ".cursor/rules": None,
    },
}


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

    # Clean existing .mdc files
    for mdc in rules_dir.glob("*.mdc"):
        mdc.unlink()

    for skill_path in skills_dir.iterdir():
        if not skill_path.is_dir():
            continue

        skill_md = skill_path / "SKILL.md"
        if not skill_md.exists():
            warn(f"Missing SKILL.md for {skill_path.name}")
            continue

        out_file = rules_dir / f"{skill_path.name}.mdc"
        shutil.copy(skill_md, out_file)
        info(f"Skill {skill_path.name}: SKILL.md -> {out_file.name}")


def merge_mcp_configs(source: Path, target: Path):
    """Merge MCP servers from source into target."""
    if not source.exists():
        warn(f"Source MCP config not found: {source}")
        return

    # Load or create target config
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
    skipped = []

    for name, server in source_servers.items():
        if name in target_servers:
            skipped.append(name)
        else:
            target_servers[name] = server
            added.append(name)

    with open(target, "w") as f:
        json.dump(target_cfg, f, indent=2)
        f.write("\n")

    info(f"MCP servers added: {', '.join(added) or 'none'}")
    if skipped:
        info(f"MCP servers skipped (existing): {', '.join(skipped)}")


def confirm(skip: bool = False) -> bool:
    """Ask for user confirmation."""
    info("Planned actions:")
    print("  - Symlink skills to Claude (workspace)")
    print("  - Generate .mdc rules for Cursor from skills")
    print()

    if skip:
        info("Skipping confirmation (--yes)")
        return True

    if not sys.stdin.isatty():
        warn("No TTY available; use --yes to skip confirmation")
        return False

    reply = input("[hive] Proceed? [y/N]: ").strip().lower()
    return reply in ("y", "yes")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Hive release script")
    parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation")
    args = parser.parse_args()

    info(f"Workspace root: {WORKSPACE_ROOT}")
    info(f"Hive directory: {HIVE_DIR}")

    if not confirm(skip=args.yes):
        info("Cancelled")
        return 1

    # Ensure source exists
    if not SKILLS_DIR.exists():
        warn(f"Skills directory not found: {SKILLS_DIR}")
        return 1

    # Create workspace symlinks
    for rel_path, target in TARGETS["workspace"].items():
        if target is None:
            continue
        link_path = WORKSPACE_ROOT / rel_path
        create_symlink(target, link_path, f"Workspace {rel_path}")

    # Create hive symlinks
    for rel_path, target in TARGETS["hive"].items():
        if target is None:
            continue
        link_path = HIVE_DIR / rel_path
        create_symlink(target, link_path, f"Hive {rel_path}")

    # Build Cursor rules from skills
    hive_rules = HIVE_DIR / ".cursor" / "rules"
    build_cursor_rules(SKILLS_DIR, hive_rules)

    # Link workspace rules to hive rules
    workspace_rules = WORKSPACE_ROOT / ".cursor" / "rules"
    create_symlink(hive_rules, workspace_rules, "Workspace .cursor/rules")

    # Merge MCP configs if hive has one
    hive_mcp = HIVE_DIR / ".mcp.json"
    workspace_mcp = WORKSPACE_ROOT / ".mcp.json"
    if hive_mcp.exists():
        merge_mcp_configs(hive_mcp, workspace_mcp)

    info("Release complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
