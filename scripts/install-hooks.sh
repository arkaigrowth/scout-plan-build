#!/bin/bash
#
# Install git hooks for Scout Plan Build MVP
#
# Run once after cloning: ./scripts/install-hooks.sh
#
# This script:
# 1. Creates the .git/hooks directory if needed
# 2. Copies/links the pre-commit hook
# 3. Makes hooks executable
#

set -e

# Find the repository root
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"

if [ -z "$REPO_ROOT" ]; then
    echo "Error: Not in a git repository"
    exit 1
fi

HOOKS_DIR="$REPO_ROOT/.git/hooks"
SOURCE_HOOKS="$REPO_ROOT/scripts/hooks"

echo "Installing git hooks..."
echo "  Repository: $REPO_ROOT"
echo "  Hooks dir:  $HOOKS_DIR"

# Ensure hooks directory exists
mkdir -p "$HOOKS_DIR"

# Install pre-commit hook
if [ -f "$SOURCE_HOOKS/pre-commit" ]; then
    # Copy the hook (symlinks can have issues with some git configurations)
    cp "$SOURCE_HOOKS/pre-commit" "$HOOKS_DIR/pre-commit"
    chmod +x "$HOOKS_DIR/pre-commit"
    echo "  Installed: pre-commit"
else
    echo "  Warning: pre-commit hook source not found at $SOURCE_HOOKS/pre-commit"
fi

# Make the Python script executable
PYTHON_SCRIPT="$REPO_ROOT/scripts/update-research-index.py"
if [ -f "$PYTHON_SCRIPT" ]; then
    chmod +x "$PYTHON_SCRIPT"
    echo "  Made executable: update-research-index.py"
fi

echo ""
echo "Git hooks installed successfully!"
echo ""
echo "The pre-commit hook will now check that the research index"
echo "is up-to-date when you commit changes to ai_docs/research/."
echo ""
echo "To manually update the index, run:"
echo "  python scripts/update-research-index.py"
echo ""
