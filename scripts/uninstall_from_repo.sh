#!/bin/bash
# Uninstall Scout-Plan-Build from a repository
# Usage: ./uninstall_from_repo.sh /path/to/repo

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🗑️  Scout-Plan-Build Uninstaller"
echo "==============================="
echo ""

if [ $# -eq 0 ]; then
    echo -e "${RED}Error: Please provide repository path${NC}"
    echo "Usage: $0 /path/to/repo"
    exit 1
fi

TARGET_REPO="$1"

if [ ! -d "$TARGET_REPO" ]; then
    echo -e "${RED}Error: Directory $TARGET_REPO does not exist${NC}"
    exit 1
fi

cd "$TARGET_REPO"

echo -e "${YELLOW}WARNING: This will remove Scout-Plan-Build components from:${NC}"
echo "  $TARGET_REPO"
echo ""
echo "Files/directories to be removed:"
echo "  • adws/"
echo "  • .claude/commands/scout*.md"
echo "  • .claude/commands/plan_w_docs*.md"
echo "  • .claude/commands/build*.md"
echo "  • scripts/validate_pipeline.sh"
echo "  • test_installation.py"
echo "  • .env.template (if exists)"
echo "  • .adw_config.json (if exists)"
echo "  • CLAUDE.md (if it was created by installer)"
echo ""
echo "Directories that may have content (will only remove if empty):"
echo "  • scout_outputs/ (old structure)"
echo "  • ai_docs/scout/ (new structure)"
echo "  • specs/"
echo ""
read -p "Continue? (yes/no) " -r
echo

if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# Track what was removed
REMOVED=()
KEPT=()

# Remove core modules
if [ -d "adws" ]; then
    rm -rf adws
    REMOVED+=("adws/")
fi

# Remove slash commands
for cmd in .claude/commands/scout*.md .claude/commands/plan_w_docs*.md .claude/commands/build*.md; do
    if [ -f "$cmd" ]; then
        rm -f "$cmd"
        REMOVED+=("$(basename $cmd)")
    fi
done

# Remove scripts
if [ -f "scripts/validate_pipeline.sh" ]; then
    rm -f scripts/validate_pipeline.sh
    REMOVED+=("scripts/validate_pipeline.sh")
fi

# Remove test file
if [ -f "test_installation.py" ]; then
    rm -f test_installation.py
    REMOVED+=("test_installation.py")
fi

# Remove config files (be careful)
if [ -f ".env.template" ]; then
    rm -f .env.template
    REMOVED+=(".env.template")
fi

if [ -f ".adw_config.json" ]; then
    echo -e "${YELLOW}Found .adw_config.json${NC}"
    read -p "Remove .adw_config.json? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f .adw_config.json
        REMOVED+=(".adw_config.json")
    else
        KEPT+=(".adw_config.json")
    fi
fi

# Check CLAUDE.md
if [ -f "CLAUDE.md" ]; then
    if grep -q "Scout-Plan-Build" CLAUDE.md 2>/dev/null; then
        echo -e "${YELLOW}Found CLAUDE.md with Scout-Plan-Build content${NC}"
        read -p "Remove CLAUDE.md? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -f CLAUDE.md
            REMOVED+=("CLAUDE.md")
        else
            KEPT+=("CLAUDE.md")
        fi
    fi
fi

# Clean up empty directories (only if they're empty)
echo ""
echo "Checking for empty directories..."

if [ -d "scout_outputs" ]; then
    if [ -z "$(ls -A scout_outputs 2>/dev/null)" ]; then
        rmdir scout_outputs
        REMOVED+=("scout_outputs/ (was empty)")
    else
        KEPT+=("scout_outputs/ (has content)")
    fi
fi

if [ -d "ai_docs/scout" ]; then
    if [ -z "$(ls -A ai_docs/scout 2>/dev/null)" ]; then
        rmdir ai_docs/scout
        REMOVED+=("ai_docs/scout/ (was empty)")
    else
        KEPT+=("ai_docs/scout/ (has content)")
    fi
fi

if [ -d "specs" ]; then
    if [ -z "$(ls -A specs 2>/dev/null)" ]; then
        rmdir specs
        REMOVED+=("specs/ (was empty)")
    else
        KEPT+=("specs/ (has content - preserved)")
    fi
fi

if [ -d ".claude/commands" ]; then
    if [ -z "$(ls -A .claude/commands 2>/dev/null)" ]; then
        rmdir .claude/commands
        REMOVED+=(".claude/commands/ (was empty)")
    fi
fi

# Summary
echo ""
echo -e "${GREEN}✨ Uninstall Complete!${NC}"
echo "======================"
echo ""

if [ ${#REMOVED[@]} -gt 0 ]; then
    echo "Removed:"
    for item in "${REMOVED[@]}"; do
        echo "  ✓ $item"
    done
fi

echo ""

if [ ${#KEPT[@]} -gt 0 ]; then
    echo -e "${YELLOW}Kept (had content or user choice):${NC}"
    for item in "${KEPT[@]}"; do
        echo "  • $item"
    done
fi

echo ""
echo "The repository has been cleaned of Scout-Plan-Build components."
echo "Your existing code and data files are untouched."