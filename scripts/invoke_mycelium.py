#!/usr/bin/env python3
"""
invoke_mycelium.py
Invokes Mycelium (Gemini 2.5) for PRD and Implementation Plan creation
Usage: python3 invoke_mycelium.py <file_path> [doc_type]
"""

import sys
import os
from pathlib import Path

try:
    import google.generativeai as genai
except ImportError:
    print("Error: google-generativeai not installed")
    print("Install with: pip install google-generativeai")
    sys.exit(1)

# Colors for output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
NC = '\033[0m' # No Color

def load_env():
    """Load .env file from workspace root"""
    script_dir = Path(__file__).parent.resolve()
    workspace_root = script_dir.parent.parent  # .claude/scripts -> .claude -> root
    env_file = workspace_root / ".env"

    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())

def main():
    # Load .env file
    load_env()

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

    # Configure Gemini API
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print(f"{RED}Error: No API key found{NC}")
        print("Set GEMINI_API_KEY or GOOGLE_API_KEY environment variable")
        print("Get API key from: https://makersuite.google.com/app/apikey")
        sys.exit(1)

    genai.configure(api_key=api_key)

    # Paths
    cwd = Path.cwd()
    workspace_root = cwd
    
    # If we are not in root (e.g. in .claude/scripts), find root
    if not (workspace_root / "GEMINI.md").exists():
         # Try to derive from script location
         script_dir = Path(__file__).parent.resolve()
         # .claude/scripts -> .claude -> root
         potential_root = script_dir.parent.parent
         if (potential_root / "GEMINI.md").exists():
             workspace_root = potential_root
         else:
             # Fallback to the path used in bash script if CWD/relative fails
             workspace_root = Path("/Users/gpublica/workspace/skywalking")

    GEMINI_md = workspace_root / "GEMINI.md"
    # Output file pattern for Mycelium
    output_file = file_path.parent / f"{file_path.name}-mycelium-output.md"

    # Verify GEMINI.md exists
    if not GEMINI_md.exists():
        print(f"{RED}Error: GEMINI.md not found at {GEMINI_md}{NC}")
        sys.exit(1)

    print(f"{YELLOW}[Mycelium] Reading document: {file_path}{NC}")

    try:
        document_content = file_path.read_text(encoding='utf-8')
        GEMINI_context = GEMINI_md.read_text(encoding='utf-8')
    except Exception as e:
        print(f"{RED}Error reading files: {e}{NC}")
        sys.exit(1)

    # Construct the prompt
    prompt = f"""Your name, role, personality, and operational guidelines are defined in GEMINI.md below:

---
{GEMINI_context}
---

TASK: Analyze the following {doc_type} and generate a comprehensive PRD and Implementation Plan.

INPUT DOCUMENT:
---
{document_content}
---

INSTRUCTIONS:
1. Analyze this document from your perspective as Mycelium (Gemini 2.5).
2. Your goal is to produce a detailed PRD (Product Requirements Document) and Implementation Plan.
3. Follow the structure defined in GEMINI.md for Mycelium's outputs or the "Project Skeleton" section.
4. Focus on:
   - Detailed system architecture
   - Clear success metrics
   - Step-by-step implementation plan
   - Agent delegation (which parts go to Aurora, Kokoro, Pixel, Flux, etc.)
   - Risk assessment

5. Be thorough and structured.

OUTPUT: Generate a complete markdown document.
Do NOT include any preamble or meta-commentary. Start directly with the markdown document.
"""

    print(f"{YELLOW}[Mycelium] Invoking Gemini API for analysis...{NC}")

    try:
        # Configure model - use env var or default to gemini-2.5-flash
        model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

        # Create model instance
        model = genai.GenerativeModel(model_name)

        # Generate response
        print(f"{YELLOW}[Mycelium] Using model: {model_name}{NC}")
        response = model.generate_content(prompt)

        gemini_output = response.text
        
        # Write output to file
        if not gemini_output:
             print(f"{RED}Error: No output received from Gemini{NC}")
             sys.exit(1)

        output_file.write_text(gemini_output, encoding='utf-8')

        print(f"{GREEN}[Mycelium] Output generated: {output_file}{NC}")
        print(f"{GREEN}[Mycelium] Analysis complete{NC}")
        
        # Output the file path
        print(str(output_file))

    except Exception as e:
        print(f"{RED}Error during execution: {e}{NC}")
        sys.exit(1)

if __name__ == "__main__":
    main()

