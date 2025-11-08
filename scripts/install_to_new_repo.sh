#!/bin/bash
# Portable Installation Script for Scout-Plan-Build System
# Usage: ./install_to_new_repo.sh /path/to/target/repo

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🚀 Scout-Plan-Build Portable Installer"
echo "======================================"
echo ""

# Check arguments
if [ $# -eq 0 ]; then
    echo -e "${RED}Error: Please provide target repository path${NC}"
    echo "Usage: $0 /path/to/target/repo"
    exit 1
fi

TARGET_REPO="$1"
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Verify target is a git repo
if [ ! -d "$TARGET_REPO/.git" ]; then
    echo -e "${YELLOW}Warning: $TARGET_REPO is not a git repository${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "📦 Installing from: $SOURCE_DIR"
echo "📍 Installing to:   $TARGET_REPO"
echo ""

# Create required directories
echo "📁 Creating directory structure..."
mkdir -p "$TARGET_REPO/specs"
mkdir -p "$TARGET_REPO/ai_docs/scout"
mkdir -p "$TARGET_REPO/ai_docs/build_reports"
mkdir -p "$TARGET_REPO/.claude/commands"
mkdir -p "$TARGET_REPO/.claude/state"
mkdir -p "$TARGET_REPO/scripts"

# Copy core modules (100% portable)
echo "📋 Copying core modules..."
cp -r "$SOURCE_DIR/adws" "$TARGET_REPO/"

# Copy working slash commands
echo "📝 Copying slash commands..."
# Only copy the WORKING commands, not broken ones
cp "$SOURCE_DIR/.claude/commands/plan_w_docs.md" "$TARGET_REPO/.claude/commands/" 2>/dev/null || true
cp "$SOURCE_DIR/.claude/commands/plan_w_docs_improved.md" "$TARGET_REPO/.claude/commands/" 2>/dev/null || true
cp "$SOURCE_DIR/.claude/commands/build_adw.md" "$TARGET_REPO/.claude/commands/" 2>/dev/null || true
cp "$SOURCE_DIR/.claude/commands/scout.md" "$TARGET_REPO/.claude/commands/" 2>/dev/null || true

# Copy hooks for observability
echo "🪝 Copying hooks for logging and validation..."
cp -r "$SOURCE_DIR/.claude/hooks" "$TARGET_REPO/.claude/" 2>/dev/null || true

# Copy skills for workflow orchestration
echo "🎯 Copying skills (workflow building blocks)..."
cp -r "$SOURCE_DIR/.claude/skills" "$TARGET_REPO/.claude/" 2>/dev/null || true

# Copy validation script
echo "✅ Copying validation tools..."
cp "$SOURCE_DIR/scripts/validate_pipeline.sh" "$TARGET_REPO/scripts/"
chmod +x "$TARGET_REPO/scripts/validate_pipeline.sh"

# Create .env template
echo "🔑 Creating .env template..."
cat > "$TARGET_REPO/.env.template" << 'EOF'
# Scout-Plan-Build Configuration
# Copy to .env and fill in your values

# Required
ANTHROPIC_API_KEY=sk-ant-...
GITHUB_PAT=ghp_...
GITHUB_REPO_URL=https://github.com/owner/repo

# Important - prevents token limit errors
CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768

# Optional
E2B_API_KEY=
R2_ACCOUNT_ID=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_NAME=
EOF

# Create project-specific config
echo "⚙️ Creating configuration file..."
cat > "$TARGET_REPO/.adw_config.json" << EOF
{
  "project": {
    "name": "$(basename "$TARGET_REPO")",
    "type": "auto-detect"
  },
  "paths": {
    "specs": "specs/",
    "agents": "agents/",
    "ai_docs": "ai_docs/",
    "app_code": ".",
    "allowed": ["specs", "agents", "ai_docs", "app", "src", "lib"]
  },
  "workflow": {
    "use_github": true,
    "auto_branch": true,
    "branch_prefix": "feature/"
  }
}
EOF

# Create simplified CLAUDE.md
echo "📖 Creating project instructions..."
cat > "$TARGET_REPO/CLAUDE.md" << 'EOF'
# Scout-Plan-Build Workflow Instructions

## Quick Start

### 1. Setup Environment
```bash
cp .env.template .env
# Edit .env with your API keys
export $(grep -v '^#' .env | xargs)
```

### 2. Basic Workflow

```bash
# Find relevant files for your task
python adws/scout_simple.py "implement user authentication"

# Create a plan/spec
/plan_w_docs "implement user auth" "" "ai_docs/scout/relevant_files.json"

# Build from the spec
/build_adw "specs/issue-001-*.md"
```

### 3. Validate System
```bash
./scripts/validate_pipeline.sh
```

## What Works
✅ Scout with Task agents (not external tools)
✅ Plan generation with validation
✅ Build with error handling
✅ Git operations and branching

## Common Tasks

| Task | Command |
|------|---------|
| Find files | `Task(subagent_type="explore", prompt="...")` |
| Create spec | `/plan_w_docs "task" "docs" "files.json"` |
| Build code | `/build_adw "specs/plan.md"` |
| Validate | `./scripts/validate_pipeline.sh` |

## Customization

Edit `.adw_config.json` to:
- Change directory names
- Add allowed paths
- Configure git behavior
EOF

# Install Python dependencies
echo "📦 Checking Python dependencies..."
if command -v uv &> /dev/null; then
    echo "   Using uv for dependency management"
    cd "$TARGET_REPO"
    if [ ! -f "pyproject.toml" ]; then
        # Create minimal pyproject.toml if missing
        cat > pyproject.toml << 'EOF'
[project]
name = "scout-plan-build"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "pydantic>=2.0",
    "python-dotenv",
    "gitpython",
    "anthropic",
    "boto3",
]
EOF
    fi
    echo "   Run 'uv sync' to install dependencies"
else
    echo "   ⚠️ Install uv for dependency management: https://github.com/astral-sh/uv"
fi

# Create test file
echo "🧪 Creating test script..."
cat > "$TARGET_REPO/test_installation.py" << 'EOF'
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
EOF

chmod +x "$TARGET_REPO/test_installation.py"

# Final summary
echo ""
echo "✨ Installation Complete!"
echo "========================"
echo ""
echo "📁 Installed to: $TARGET_REPO"
echo ""
echo "Next steps:"
echo "1. cd $TARGET_REPO"
echo "2. cp .env.template .env"
echo "3. Edit .env with your API keys"
echo "4. export \$(grep -v '^#' .env | xargs)"
echo "5. python test_installation.py"
echo "6. ./scripts/validate_pipeline.sh"
echo ""
echo "📚 Documentation:"
echo "   • CLAUDE.md - Quick start guide"
echo "   • .adw_config.json - Customize paths"
echo "   • .env.template - Configuration"
echo ""
echo -e "${GREEN}Ready to use!${NC}"