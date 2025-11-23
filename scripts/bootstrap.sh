#!/bin/bash
# Scout-Plan-Build Framework Bootstrap
#
# Usage:
#   curl -sSL https://raw.githubusercontent.com/USER/scout-plan-build/main/scripts/bootstrap.sh | bash
#
# Or with target directory:
#   curl -sSL https://...bootstrap.sh | bash -s -- /path/to/repo

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration - Framework repository
REPO_URL="${SPB_REPO_URL:-https://github.com/arkaigrowth/scout-plan-build}"
BRANCH="${SPB_BRANCH:-main}"
RAW_URL="https://raw.githubusercontent.com/${REPO_URL#https://github.com/}/${BRANCH}"

echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     🚀 Scout-Plan-Build Framework Bootstrap               ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Detect target directory
TARGET_DIR="${1:-$(pwd)}"

echo -e "📍 Target: ${GREEN}$TARGET_DIR${NC}"
echo ""

# Step 1: Install user-level command (works in ANY repo)
echo -e "${YELLOW}Step 1: Installing user-level /init-framework command...${NC}"
mkdir -p ~/.claude/commands

if curl -sSL "${RAW_URL}/.claude/commands/init-framework.md" -o ~/.claude/commands/init-framework.md 2>/dev/null; then
    echo -e "   ${GREEN}✓${NC} Installed to ~/.claude/commands/init-framework.md"
    echo -e "   ${GREEN}✓${NC} Now available as /init-framework in ANY repo!"
else
    echo -e "   ${RED}✗${NC} Failed to download init-framework.md"
    echo -e "   ${YELLOW}→${NC} You may need to update REPO_URL in this script"
fi

echo ""

# Step 2: Ask about full installation
echo -e "${YELLOW}Step 2: Full framework installation${NC}"
echo ""
echo "Options:"
echo "  1) Install full framework to current directory ($TARGET_DIR)"
echo "  2) Install full framework to different directory"
echo "  3) Skip (just use /init-framework interactively later)"
echo ""

read -p "Choose [1/2/3]: " choice

case $choice in
    1)
        INSTALL_DIR="$TARGET_DIR"
        ;;
    2)
        read -p "Enter target directory path: " INSTALL_DIR
        ;;
    3)
        echo ""
        echo -e "${GREEN}✨ Bootstrap complete!${NC}"
        echo ""
        echo "To set up a project, run:"
        echo -e "  ${BLUE}/init-framework${NC}  (in Claude Code)"
        echo ""
        exit 0
        ;;
    *)
        INSTALL_DIR="$TARGET_DIR"
        ;;
esac

# Verify/create target directory
if [ ! -d "$INSTALL_DIR" ]; then
    read -p "Directory doesn't exist. Create it? [y/N]: " create
    if [[ $create =~ ^[Yy]$ ]]; then
        mkdir -p "$INSTALL_DIR"
    else
        echo "Aborted."
        exit 1
    fi
fi

# Step 3: Download and run full installer
echo ""
echo -e "${YELLOW}Step 3: Downloading full installer...${NC}"

TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

# Clone just the scripts we need (shallow, sparse)
if command -v git &> /dev/null; then
    echo "   Cloning framework repository..."
    git clone --depth 1 --filter=blob:none --sparse "$REPO_URL" spb-framework 2>/dev/null || {
        echo -e "   ${RED}✗${NC} Git clone failed. Trying direct download..."
        # Fallback: download files directly
        mkdir -p spb-framework/scripts
        curl -sSL "${RAW_URL}/scripts/install_to_new_repo.sh" -o spb-framework/scripts/install_to_new_repo.sh
    }

    if [ -d "spb-framework" ]; then
        cd spb-framework
        git sparse-checkout set scripts adws agents .claude agent_runs 2>/dev/null || true
        git checkout 2>/dev/null || true
    fi
else
    echo -e "   ${YELLOW}⚠${NC} Git not found, using direct download..."
    mkdir -p spb-framework
    curl -sSL "${RAW_URL}/scripts/install_to_new_repo.sh" -o spb-framework/scripts/install_to_new_repo.sh
fi

# Run the installer
echo ""
echo -e "${YELLOW}Step 4: Running installer...${NC}"
echo ""

if [ -f "spb-framework/scripts/install_to_new_repo.sh" ]; then
    chmod +x spb-framework/scripts/install_to_new_repo.sh
    cd spb-framework
    ./scripts/install_to_new_repo.sh "$INSTALL_DIR"
else
    echo -e "${RED}✗${NC} Installer not found. Manual installation required."
    echo ""
    echo "Clone the repo manually:"
    echo "  git clone $REPO_URL"
    echo "  cd $(basename $REPO_URL)"
    echo "  ./scripts/install_to_new_repo.sh $INSTALL_DIR"
fi

# Cleanup
cd /
rm -rf "$TEMP_DIR"

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     ✨ Installation Complete!                             ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Next steps:"
echo -e "  1. ${BLUE}cd $INSTALL_DIR${NC}"
echo -e "  2. ${BLUE}cp .env.template .env${NC}  (add your API keys)"
echo -e "  3. ${BLUE}/init-framework${NC}  (in Claude Code for interactive setup)"
echo ""
echo "Or run the test:"
echo -e "  ${BLUE}python test_installation.py${NC}"
echo ""
