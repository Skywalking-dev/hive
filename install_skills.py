#!/usr/bin/env python3
"""
Install third-party skills into skills/.
Downloads skills from their original repos and places them in the right directory.
"""

import sys
import json
import shutil
import tempfile
import subprocess
from pathlib import Path

SKILLS_DIR = Path(__file__).parent / "skills"

# Third-party skill registry
# Each entry: source repo, subdirectory in repo, skills to install
REGISTRY = {
    "n8n-skills": {
        "repo": "https://github.com/czlonkowski/n8n-skills.git",
        "path": "skills",
        "author": "Romuald Członkowski",
        "license": "MIT",
        "skills": [
            "n8n-workflow-patterns",
            "n8n-code-javascript",
            "n8n-code-python",
            "n8n-expression-syntax",
            "n8n-node-configuration",
            "n8n-validation-expert",
            "n8n-mcp-tools-expert",
        ],
    },
    "anthropic-skills": {
        "repo": "https://github.com/anthropics/claude-code-skills.git",
        "path": "skills",
        "author": "Anthropic",
        "license": "Proprietary",
        "skills": [
            "pdf-anthropic",
            "skill-creator",
            "frontend-design",
        ],
    },
}


def info(msg: str):
    print(f"  {msg}")


def install_from_repo(name: str, entry: dict, force: bool = False) -> int:
    """Clone repo to temp dir, copy skills into skills/."""
    repo = entry["repo"]
    src_path = entry["path"]
    skills = entry["skills"]

    print(f"\n[{name}] {repo}")
    print(f"  Author: {entry['author']} | License: {entry['license']}")

    # Check which skills need installing
    to_install = []
    for skill in skills:
        dest = SKILLS_DIR / skill
        if dest.exists() and not force:
            info(f"{skill}: already installed (use --force to overwrite)")
        else:
            to_install.append(skill)

    if not to_install:
        info("Nothing to install.")
        return 0

    # Clone to temp dir
    info(f"Cloning {repo}...")
    with tempfile.TemporaryDirectory() as tmp:
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", "--quiet", repo, tmp],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as e:
            info(f"Failed to clone: {e.stderr.decode().strip()}")
            return 1

        src_dir = Path(tmp) / src_path
        if not src_dir.exists():
            info(f"Source path '{src_path}' not found in repo")
            return 1

        installed = 0
        for skill in to_install:
            skill_src = src_dir / skill
            if not skill_src.exists():
                info(f"{skill}: not found in repo, skipping")
                continue

            dest = SKILLS_DIR / skill
            if dest.exists():
                shutil.rmtree(dest)

            shutil.copytree(skill_src, dest)
            info(f"{skill}: installed")
            installed += 1

        info(f"Done — {installed} skill(s) installed.")
        return 0


def list_skills():
    """List all available third-party skills."""
    print("Available third-party skills:\n")
    for name, entry in REGISTRY.items():
        print(f"  [{name}] ({entry['license']})")
        for skill in entry["skills"]:
            dest = SKILLS_DIR / skill
            status = "installed" if dest.exists() else "not installed"
            print(f"    {skill:30s} {status}")
    print(f"\nInstall with: python install_skills.py [--all | <collection>]")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Install third-party skills for Hive")
    parser.add_argument("collection", nargs="?", help="Skill collection to install (e.g. n8n-skills)")
    parser.add_argument("--all", action="store_true", help="Install all collections")
    parser.add_argument("--list", action="store_true", help="List available skills")
    parser.add_argument("--force", action="store_true", help="Overwrite existing skills")
    args = parser.parse_args()

    if args.list or (not args.collection and not args.all):
        list_skills()
        return 0

    collections = REGISTRY.keys() if args.all else [args.collection]

    for name in collections:
        if name not in REGISTRY:
            print(f"Unknown collection: {name}")
            print(f"Available: {', '.join(REGISTRY.keys())}")
            return 1
        result = install_from_repo(name, REGISTRY[name], args.force)
        if result != 0:
            return result

    return 0


if __name__ == "__main__":
    sys.exit(main())
