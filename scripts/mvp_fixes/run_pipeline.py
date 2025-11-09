#!/usr/bin/env python3
"""
WORKING PIPELINE - Chains Scout→Plan→Build with what actually works.
This is your go-to script for the full workflow.
"""

import subprocess
import sys
import json
from pathlib import Path

def run_scout(task: str) -> bool:
    """Run the working scout."""
    print("\n🔍 PHASE 1: SCOUT")
    print("-" * 40)

    result = subprocess.run(
        ["python3", "adws/scout_simple.py", task],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print(result.stdout)
        return True
    else:
        print(f"❌ Scout failed: {result.stderr}")
        return False

def run_plan(task: str, docs_url: str = "") -> str:
    """Run the plan phase."""
    print("\n📝 PHASE 2: PLAN")
    print("-" * 40)

    # Check if scout output exists
    scout_file = "ai_docs/scout/relevant_files.json"
    if not Path(scout_file).exists():
        print("❌ No scout output found. Run scout first!")
        return None

    # Build plan command
    cmd = [
        "python3", "adws/adw_plan.py",
        task,
        docs_url if docs_url else "https://docs.python.org",
        scout_file
    ]

    print(f"Running: {' '.join(cmd[:3])}...")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        # Extract spec file path from output
        for line in result.stdout.split('\n'):
            if 'specs/' in line and '.md' in line:
                spec_file = line.strip()
                print(f"✅ Plan created: {spec_file}")
                return spec_file
        print("✅ Plan completed (check specs/ directory)")
        return "specs/"  # Return directory if can't find specific file
    else:
        print(f"❌ Plan failed: {result.stderr[:500]}")
        return None

def run_build(spec_file: str) -> bool:
    """Run the build phase."""
    print("\n🔨 PHASE 3: BUILD")
    print("-" * 40)

    if not spec_file or not Path(spec_file).exists():
        # Try to find most recent spec
        specs = sorted(Path("specs/").glob("*.md"), key=lambda x: x.stat().st_mtime)
        if specs:
            spec_file = str(specs[-1])
            print(f"Using most recent spec: {spec_file}")
        else:
            print("❌ No spec file found!")
            return False

    cmd = ["python3", "adws/adw_build.py", spec_file]
    print(f"Building from: {spec_file}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ Build completed!")
        print(result.stdout[:500])  # First 500 chars
        return True
    else:
        print(f"❌ Build failed: {result.stderr[:500]}")
        return False

def main():
    """Run the complete pipeline."""
    if len(sys.argv) < 2:
        print("""
Usage: python run_pipeline.py "your task description" [docs_url]

Examples:
  python run_pipeline.py "Add user authentication"
  python run_pipeline.py "Create REST API" "https://fastapi.tiangolo.com"
        """)
        sys.exit(1)

    task = sys.argv[1]
    docs_url = sys.argv[2] if len(sys.argv) > 2 else ""

    print("=" * 60)
    print("🚀 RUNNING SCOUT→PLAN→BUILD PIPELINE")
    print("=" * 60)
    print(f"Task: {task}")
    if docs_url:
        print(f"Docs: {docs_url}")

    # Run pipeline
    success = True

    # Scout
    if not run_scout(task):
        print("\n⚠️  Scout failed, but you can manually create relevant_files.json")
        success = False
    else:
        # Plan (only if scout succeeded)
        spec_file = run_plan(task, docs_url)
        if not spec_file:
            print("\n⚠️  Plan failed. Check the error above.")
            success = False
        else:
            # Build (only if plan succeeded)
            if not run_build(spec_file):
                print("\n⚠️  Build failed. Check the spec file and try manually.")
                success = False

    # Summary
    print("\n" + "=" * 60)
    if success:
        print("✅ PIPELINE COMPLETE!")
        print("\nNext steps:")
        print("  1. Review the changes: git diff")
        print("  2. Test: python -m pytest")
        print("  3. Commit: git add . && git commit -m 'feat: {task}'")
        print("  4. Push: git push")
    else:
        print("⚠️  PIPELINE INCOMPLETE - See errors above")
        print("\nDebug tips:")
        print("  • Check scout output: cat ai_docs/scout/relevant_files.json")
        print("  • Check specs: ls -la specs/")
        print("  • Run health check: python check_health.py")
    print("=" * 60)

if __name__ == "__main__":
    main()