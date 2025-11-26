#!/usr/bin/env python3
"""Test Scout-Plan-Build installation"""

import os
import sys
from pathlib import Path

def test_installation():
    """Verify installation is complete"""

    print("🧪 Testing Scout-Plan-Build Installation")
    print("=" * 40)

    errors = []
    warnings = []

    # Check directories
    required_dirs = ["specs", "agents", "ai_docs", ".claude/commands", "adws"]
    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            errors.append(f"Missing directory: {dir_name}")
        else:
            print(f"✅ Directory exists: {dir_name}")

    # Check core modules
    if Path("adws/adw_plan.py").exists():
        print("✅ Core modules installed")
    else:
        errors.append("Core modules missing")

    # Check environment
    if Path(".env").exists():
        print("✅ .env file exists")
        if not os.getenv("ANTHROPIC_API_KEY"):
            warnings.append("ANTHROPIC_API_KEY not set in environment")
    else:
        warnings.append(".env file not found (copy from .env.template)")

    # Check commands
    if Path(".claude/commands/plan_w_docs.md").exists():
        print("✅ Slash commands installed")
    else:
        errors.append("Slash commands missing")

    # Results
    print("\n" + "=" * 40)

    if errors:
        print("❌ Installation FAILED:")
        for error in errors:
            print(f"   - {error}")
        return False

    if warnings:
        print("⚠️ Warnings:")
        for warning in warnings:
            print(f"   - {warning}")

    print("\n✨ Installation successful!")
    print("\nNext steps:")
    print("1. Copy .env.template to .env and add your API keys")
    print("2. Run: export $(grep -v '^#' .env | xargs)")
    print("3. Test with: ./scripts/validate_pipeline.sh")

    return True

if __name__ == "__main__":
    success = test_installation()
    sys.exit(0 if success else 1)
