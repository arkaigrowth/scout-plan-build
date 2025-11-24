#!/bin/bash
# Setup script for dependency-tracer v2

echo "🔧 Dependency Tracer v2 - Setup"
echo "================================"
echo ""

# Check if brew is available
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found. Install from: https://brew.sh"
    exit 1
fi

echo "Installing required tools via Homebrew..."
echo ""

# Install core tools
echo "→ ripgrep (fast text search)"
brew install ripgrep

echo "→ ast-grep (structural code search)"
brew install ast-grep

echo "→ jq (JSON processor)"
brew install jq

echo ""
echo "✅ Setup complete!"
echo ""
echo "Tools installed:"
which rg && echo "  ✓ ripgrep"
which ast-grep && echo "  ✓ ast-grep"
which jq && echo "  ✓ jq"
which python3 && echo "  ✓ python3"

echo ""
echo "Next step: Run validation test"
echo "  bash scripts/test_skill.sh"
