#!/usr/bin/env python3
"""
invoke_forge.py
Invokes Forge (GPT-5 via Codex CLI) for technical review and feedback
Usage: python3 invoke_forge.py <file_path> [doc_type]
"""

import sys
import os
import shutil
import subprocess
from pathlib import Path

# Colors for output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
NC = '\033[0m' # No Color

def main():
    # Arguments
    if len(sys.argv) < 2:
        print(f"{RED}Error: No file path provided{NC}")
        print(f"Usage: {sys.argv[0]} <file_path> [doc_type]")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    doc_type = sys.argv[2] if len(sys.argv) > 2 else "document"

    # Validation
    if not file_path.is_file():
        print(f"{RED}Error: File not found: {file_path}{NC}")
        sys.exit(1)

    # Check if codex CLI is available
    if not shutil.which("codex"):
        print(f"{RED}Error: Codex CLI not found{NC}")
        print("Please ensure:")
        print("  1. Codex CLI is installed")
        print("  2. 'codex' command is in PATH")
        print("  3. Authentication is configured")
        sys.exit(1)

    # Paths
    # Assuming script is in scripts/, so root is ../../
    # However, the bash script used absolute path /Users/gpublica/workspace/skywalking
    # or relative to execution. The bash script defined WORKSPACE_ROOT hardcoded.
    # We will try to find the workspace root relative to this script or current dir.
    
    # Trying to replicate bash script's hardcoded path for consistency, 
    # but dynamic is better. Bash script had: WORKSPACE_ROOT="/Users/gpublica/workspace/skywalking"
    # We will use the current working directory if it contains AGENTS.md, otherwise look relative to script.
    
    cwd = Path.cwd()
    workspace_root = cwd
    
    # If we are not in root (e.g. in .claude/scripts), find root
    if not (workspace_root / "AGENTS.md").exists():
         # Try to derive from script location
         script_dir = Path(__file__).parent.resolve()
         # .claude/scripts -> .claude -> root
         potential_root = script_dir.parent.parent
         if (potential_root / "AGENTS.md").exists():
             workspace_root = potential_root
         else:
             # Fallback to the path used in bash script if CWD/relative fails
             workspace_root = Path("/Users/gpublica/workspace/skywalking")

    agents_md = workspace_root / "AGENTS.md"
    feedback_file = file_path.parent / f"{file_path.name}-forge-feedback.md"

    # Verify AGENTS.md exists
    if not agents_md.exists():
        print(f"{RED}Error: AGENTS.md not found at {agents_md}{NC}")
        sys.exit(1)

    print(f"{YELLOW}[Forge] Reading document: {file_path}{NC}")

    try:
        document_content = file_path.read_text(encoding='utf-8')
        agents_context = agents_md.read_text(encoding='utf-8')
    except Exception as e:
        print(f"{RED}Error reading files: {e}{NC}")
        sys.exit(1)

    # Construct the prompt
    prompt = f"""Your name, role, personality, and operational guidelines are defined in AGENTS.md below:

--- AGENTS.md ---
{agents_context}
---

TASK: Review the following {doc_type} and provide structured technical feedback.

DOCUMENT TO REVIEW:
---
{document_content}
---

INSTRUCTIONS:
1. Analyze this document from your perspective as Forge (execution-focused, pragmatic, technical)
2. Follow the "Feedback Template" defined in AGENTS.md
3. Focus on:
   - Technical feasibility
   - Implementation risks (performance, security, scalability)
   - Cost/complexity trade-offs
   - Alternative approaches with pros/cons
   - Specific, actionable recommendations

4. Be constructive but honest. If something does not work, say so with alternatives.
5. Prioritize issues: HIGH (must fix), MEDIUM (should consider), LOW (nice to have)
6. Provide benchmarks or references where relevant

OUTPUT: Generate a complete markdown document following your feedback template.
Do NOT include any preamble or meta-commentary. Start directly with the markdown document.
"""

    print(f"{YELLOW}[Forge] Invoking GPT-5 for analysis...{NC}")

    try:
        # Invoke Codex CLI
        # Using 'codex exec' for non-interactive execution
        cmd = [
            "codex", "exec", 
            "--skip-git-repo-check", 
            prompt
        ]
        
        # Run command and capture output
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            check=False # We handle return code manually to print stderr
        )

        if result.returncode != 0:
            print(f"{RED}Error: Codex CLI invocation failed{NC}")
            print("Output:")
            print(result.stdout)
            print(result.stderr)
            sys.exit(1)

        codex_output = result.stdout.strip()
        
        if not codex_output and result.stderr:
             # Sometimes success might be mixed? No, if retcode 0 and empty stdout, likely issue if we expect output.
             pass

        # Write feedback to file
        if not codex_output:
             print(f"{RED}Error: No output received from Codex{NC}")
             if result.stderr:
                 print(f"Stderr: {result.stderr}")
             sys.exit(1)

        feedback_file.write_text(codex_output, encoding='utf-8')

        print(f"{GREEN}[Forge] Feedback generated: {feedback_file}{NC}")
        print(f"{GREEN}[Forge] Analysis complete{NC}")
        
        # Output the feedback file path for Mentat/Caller to read
        print(str(feedback_file))

    except Exception as e:
        print(f"{RED}Error during execution: {e}{NC}")
        sys.exit(1)

if __name__ == "__main__":
    main()

