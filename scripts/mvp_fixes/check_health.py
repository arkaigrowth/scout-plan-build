#!/usr/bin/env python3
"""
Quick health check - tells you exactly what's working and what's not.
Run this first to know your system status.
"""

import os
import subprocess
import json
from pathlib import Path

def check_command(cmd: str) -> tuple[bool, str]:
    """Check if a command exists."""
    try:
        result = subprocess.run(
            ["which", cmd],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, "Not found"
    except:
        return False, "Error checking"

def check_env_var(var: str) -> tuple[bool, str]:
    """Check if environment variable is set."""
    value = os.environ.get(var)
    if value:
        # Hide sensitive parts
        if "KEY" in var or "TOKEN" in var or "PAT" in var:
            return True, f"Set ({len(value)} chars)"
        return True, value
    return False, "Not set"

def check_file(path: str) -> bool:
    """Check if file exists."""
    return Path(path).exists()

def main():
    print("=" * 60)
    print("🏥 SCOUT PLAN BUILD - HEALTH CHECK")
    print("=" * 60)

    # Track overall health
    critical_issues = []
    warnings = []

    # Check critical environment variables
    print("\n📋 ENVIRONMENT VARIABLES:")
    print("-" * 40)

    env_vars = [
        ("ANTHROPIC_API_KEY", True),
        ("CLAUDE_CODE_MAX_OUTPUT_TOKENS", True),
        ("GITHUB_PAT", False),
        ("GITHUB_REPO_URL", False),
    ]

    for var, critical in env_vars:
        exists, value = check_env_var(var)
        status = "✅" if exists else ("❌" if critical else "⚠️")
        print(f"{status} {var}: {value}")

        if not exists:
            if critical:
                critical_issues.append(f"Missing {var}")
            else:
                warnings.append(f"Missing {var} (optional)")

    # Check critical commands
    print("\n🔧 TOOLS & COMMANDS:")
    print("-" * 40)

    commands = [
        ("git", True),
        ("python3", True),
        ("gh", False),  # GitHub CLI
        ("claude", False),  # Claude CLI
    ]

    for cmd, critical in commands:
        exists, path = check_command(cmd)
        status = "✅" if exists else ("❌" if critical else "⚠️")
        print(f"{status} {cmd}: {path if exists else 'NOT INSTALLED'}")

        if not exists:
            if critical:
                critical_issues.append(f"{cmd} not installed")
            else:
                warnings.append(f"{cmd} not installed (recommended)")

    # Check critical files
    print("\n📁 KEY FILES:")
    print("-" * 40)

    files = [
        ("adws/scout_simple.py", "Working Scout"),
        ("adws/adw_modules/validators.py", "Validation"),
        ("adws/adw_plan.py", "Plan Phase"),
        ("adws/adw_build.py", "Build Phase"),
        ("agents/scout_files/relevant_files.json", "Scout Output"),
    ]

    for filepath, desc in files:
        exists = check_file(filepath)
        status = "✅" if exists else "❌"
        print(f"{status} {desc}: {filepath}")

        if not exists and "Scout Output" not in desc:
            critical_issues.append(f"Missing {desc}")

    # Check Python imports
    print("\n🐍 PYTHON DEPENDENCIES:")
    print("-" * 40)

    try:
        from pydantic import BaseModel
        print("✅ Pydantic: Available")
    except ImportError:
        print("❌ Pydantic: Not installed")
        critical_issues.append("Pydantic not installed")

    # Summary
    print("\n" + "=" * 60)
    print("📊 HEALTH SUMMARY")
    print("=" * 60)

    if critical_issues:
        print("\n❌ CRITICAL ISSUES (Fix these first):")
        for issue in critical_issues:
            print(f"  • {issue}")
    else:
        print("\n✅ No critical issues!")

    if warnings:
        print("\n⚠️  WARNINGS (Nice to have):")
        for warning in warnings:
            print(f"  • {warning}")

    # Recommendations
    print("\n💡 QUICK FIXES:")
    print("-" * 40)

    if "gh not installed" in str(warnings + critical_issues):
        print("• Install GitHub CLI: brew install gh")

    if "ANTHROPIC_API_KEY" in str(critical_issues):
        print("• Set API key: export ANTHROPIC_API_KEY='your-key'")

    if "CLAUDE_CODE_MAX_OUTPUT_TOKENS" in str(critical_issues):
        print("• Set tokens: export CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768")

    # Test scout
    print("\n🧪 SCOUT TEST:")
    print("-" * 40)

    if check_file("adws/scout_simple.py"):
        try:
            result = subprocess.run(
                ["python3", "adws/scout_simple.py", "test"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print("✅ Scout is working!")
            else:
                print("❌ Scout failed to run")
                print(f"   Error: {result.stderr[:100]}")
        except Exception as e:
            print(f"❌ Scout test failed: {e}")
    else:
        print("❌ Scout not found")

    # Overall status
    print("\n" + "=" * 60)
    if not critical_issues:
        print("🎉 SYSTEM READY! You can use Scout→Plan→Build pipeline")
    elif len(critical_issues) <= 2:
        print("🔧 ALMOST READY! Fix critical issues above")
    else:
        print("🚧 NEEDS SETUP - Fix critical issues first")
    print("=" * 60)

if __name__ == "__main__":
    main()