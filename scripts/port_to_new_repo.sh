#!/bin/bash
# Port scout_plan_build_mvp to a new repository
# Usage: ./scripts/port_to_new_repo.sh /path/to/new/repo

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory (where scout_plan_build_mvp lives)
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_DIR="${1}"

# Banner
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Scout Plan Build MVP - Repository Port Script           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Validation
if [ -z "$TARGET_DIR" ]; then
    echo -e "${RED}Error: Target directory not specified${NC}"
    echo "Usage: $0 /path/to/new/repo"
    exit 1
fi

if [ ! -d "$TARGET_DIR" ]; then
    echo -e "${RED}Error: Target directory does not exist: $TARGET_DIR${NC}"
    exit 1
fi

if [ ! -d "$TARGET_DIR/.git" ]; then
    echo -e "${YELLOW}Warning: Target directory is not a git repository${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${GREEN}✓ Validated target directory${NC}"
echo ""

# Step 1: Copy core files
echo -e "${BLUE}[1/6] Copying core workflow system...${NC}"

if [ -d "$TARGET_DIR/adws" ]; then
    echo -e "${YELLOW}Warning: adws/ directory already exists${NC}"
    read -p "Overwrite? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$TARGET_DIR/adws"
    else
        echo -e "${RED}Aborted${NC}"
        exit 1
    fi
fi

cp -r "$SOURCE_DIR/adws" "$TARGET_DIR/"
echo -e "${GREEN}✓ Copied adws/ directory${NC}"

# Step 2: Copy slash commands
echo -e "${BLUE}[2/6] Copying slash commands...${NC}"

mkdir -p "$TARGET_DIR/.claude"

if [ -d "$TARGET_DIR/.claude/commands" ]; then
    echo -e "${YELLOW}Warning: .claude/commands/ directory already exists${NC}"
    read -p "Overwrite? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$TARGET_DIR/.claude/commands"
    else
        echo "Skipping slash commands..."
    fi
fi

if [ ! -d "$TARGET_DIR/.claude/commands" ]; then
    cp -r "$SOURCE_DIR/.claude/commands" "$TARGET_DIR/.claude/"
    echo -e "${GREEN}✓ Copied slash commands${NC}"
fi

# Step 3: Create configuration
echo -e "${BLUE}[3/6] Creating configuration...${NC}"

if [ -f "$TARGET_DIR/.env" ]; then
    echo -e "${YELLOW}Warning: .env file already exists${NC}"
    read -p "Backup and create new? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        mv "$TARGET_DIR/.env" "$TARGET_DIR/.env.backup.$(date +%s)"
        echo -e "${GREEN}✓ Backed up existing .env${NC}"
    fi
fi

if [ ! -f "$TARGET_DIR/.env" ]; then
    # Get repository URL from git
    cd "$TARGET_DIR"
    REPO_URL=$(git remote get-url origin 2>/dev/null || echo "https://github.com/owner/repo")

    # Prompt for API key
    echo ""
    read -p "Enter your Anthropic API key (or press Enter to configure later): " API_KEY

    # Create .env file
    cat > "$TARGET_DIR/.env" << EOF
# Scout Plan Build MVP Configuration
# Generated: $(date)

# ===========================================
# REQUIRED VARIABLES
# ===========================================

# Anthropic API Key for Claude Code
ANTHROPIC_API_KEY=${API_KEY:-sk-ant-your-key-here}

# GitHub Repository URL
GITHUB_REPO_URL=${REPO_URL}

# ===========================================
# CLAUDE CONFIGURATION
# ===========================================

# Claude Code CLI path (defaults to "claude" if in PATH)
CLAUDE_CODE_PATH=claude

# Maximum output tokens for Claude responses
CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768

# Maintain project working directory in bash commands
CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR=true

# ===========================================
# OPTIONAL VARIABLES
# ===========================================

# GitHub Personal Access Token (optional)
# Only needed if using different account than 'gh auth login'
# GITHUB_PAT=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# R2 Storage Configuration (optional, for screenshot uploads)
# R2_ACCESS_KEY_ID=your-r2-access-key
# R2_SECRET_ACCESS_KEY=your-r2-secret
# R2_ENDPOINT_URL=https://your-account-id.r2.cloudflarestorage.com
# R2_BUCKET_NAME=your-bucket-name
# R2_PUBLIC_URL=https://your-public-url.com
EOF

    echo -e "${GREEN}✓ Created .env configuration${NC}"
fi

# Step 4: Create directory structure
echo -e "${BLUE}[4/6] Creating directory structure...${NC}"

mkdir -p "$TARGET_DIR/specs"
mkdir -p "$TARGET_DIR/agents"
mkdir -p "$TARGET_DIR/ai_docs"
mkdir -p "$TARGET_DIR/docs"

echo -e "${GREEN}✓ Created required directories${NC}"

# Step 5: Configure validators (optional)
echo ""
echo -e "${YELLOW}Configure custom directory paths?${NC}"
echo "The system expects these directories: specs/, agents/, ai_docs/"
read -p "Use custom directory names? (y/n) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    read -p "Plans directory (default: specs): " PLANS_DIR
    read -p "State directory (default: agents): " STATE_DIR
    read -p "Docs directory (default: ai_docs): " DOCS_DIR

    PLANS_DIR=${PLANS_DIR:-specs}
    STATE_DIR=${STATE_DIR:-agents}
    DOCS_DIR=${DOCS_DIR:-ai_docs}

    # Create custom config
    cat > "$TARGET_DIR/.adw_config.json" << EOF
{
  "allowed_paths": [
    "${PLANS_DIR}/",
    "${STATE_DIR}/",
    "${DOCS_DIR}/",
    "docs/",
    "scripts/",
    "adws/",
    "src/",
    "app/"
  ],
  "specs_dir": "${PLANS_DIR}",
  "state_dir": "${STATE_DIR}",
  "scout_output_dir": "${STATE_DIR}/scout_files",
  "docs_dir": "${DOCS_DIR}"
}
EOF

    echo -e "${GREEN}✓ Created .adw_config.json${NC}"

    # Create custom directories
    mkdir -p "$TARGET_DIR/$PLANS_DIR"
    mkdir -p "$TARGET_DIR/$STATE_DIR"
    mkdir -p "$TARGET_DIR/$DOCS_DIR"

    echo -e "${GREEN}✓ Created custom directories${NC}"
fi

# Step 6: Copy documentation
echo -e "${BLUE}[5/6] Copying documentation...${NC}"

cp "$SOURCE_DIR/ai_docs/PORTABILITY_ANALYSIS.md" "$TARGET_DIR/docs/" 2>/dev/null || true
cp "$SOURCE_DIR/ai_docs/QUICK_PORT_GUIDE.md" "$TARGET_DIR/docs/" 2>/dev/null || true

if [ -f "$SOURCE_DIR/README.md" ]; then
    cp "$SOURCE_DIR/README.md" "$TARGET_DIR/docs/ADW_README.md" 2>/dev/null || true
fi

echo -e "${GREEN}✓ Copied documentation${NC}"

# Step 7: Create README for new repo
echo -e "${BLUE}[6/6] Creating setup instructions...${NC}"

cat > "$TARGET_DIR/ADW_SETUP.md" << 'EOF'
# ADW Setup Complete!

The AI Developer Workflow system has been installed in this repository.

## Next Steps

### 1. Configure Environment

Edit `.env` file and add your Anthropic API key:
```bash
nano .env
# Update ANTHROPIC_API_KEY=sk-ant-your-actual-key
```

### 2. Verify Installation

```bash
# Load environment
source .env

# Run health check
uv run adws/adw_tests/health_check.py
```

### 3. Test Workflow

```bash
# Create a test issue
gh issue create --title "Test ADW" --body "Testing the workflow"

# Run planning phase
uv run adws/adw_plan.py 1  # Replace 1 with your issue number

# Check results
ls -la specs/
git status
```

## Documentation

- `docs/QUICK_PORT_GUIDE.md` - Quick start guide
- `docs/PORTABILITY_ANALYSIS.md` - Detailed analysis
- `docs/ADW_README.md` - System overview

## Directory Structure

```
.
├── adws/                 # Workflow system
├── .claude/commands/     # Slash commands
├── specs/                # Implementation plans
├── agents/               # Agent state and logs
├── ai_docs/              # AI-generated docs
└── .env                  # Configuration
```

## Common Commands

```bash
# Plan
uv run adws/adw_plan.py <issue-number>

# Build
uv run adws/adw_build.py <issue-number> <adw-id>

# Test
uv run adws/adw_test.py <issue-number> <adw-id>

# Review
uv run adws/adw_review.py <issue-number> <adw-id>

# Full SDLC
uv run adws/adw_sdlc.py <issue-number>
```

## Support

For issues or questions, refer to the documentation in `docs/`.
EOF

echo -e "${GREEN}✓ Created ADW_SETUP.md${NC}"
echo ""

# Final summary
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Installation Complete!                                   ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Files copied to: ${BLUE}$TARGET_DIR${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. cd $TARGET_DIR"
echo "2. Edit .env to add your Anthropic API key"
echo "3. source .env"
echo "4. uv run adws/adw_tests/health_check.py"
echo "5. Read ADW_SETUP.md for detailed instructions"
echo ""
echo -e "${GREEN}Happy coding!${NC}"
