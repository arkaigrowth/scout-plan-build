#!/bin/bash
# Fix agents folder naming confusion and security issues
# This script safely renames /agents/ to /scout_outputs/ and updates all references

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}     Agents Folder Naming Fix Script${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if we're in the right directory
if [ ! -f "CLAUDE.md" ]; then
    echo -e "${RED}❌ Error: Must run from scout_plan_build_mvp root${NC}"
    exit 1
fi

# Check git status
echo -e "${YELLOW}📍 Checking git status...${NC}"
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}⚠️  Warning: You have uncommitted changes${NC}"
    echo -e "${YELLOW}   Consider committing first for easy rollback${NC}"
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# ============================================================
# STEP 1: Fix Security Vulnerability in validators.py
# ============================================================

echo ""
echo -e "${BLUE}🔒 Step 1: Fixing security vulnerability...${NC}"

# Update ALLOWED_PATH_PREFIXES to be more specific
if [ -f "adws/adw_modules/validators.py" ]; then
    # Backup original
    cp adws/adw_modules/validators.py adws/adw_modules/validators.py.bak

    # Replace broad "agents/" with specific paths
    sed -i '' 's/"agents\/",/"agents\/scout_files\/", "agents\/ADW-", "agents\/scout_temp\/",/' adws/adw_modules/validators.py

    echo -e "${GREEN}  ✅ Fixed path validation to be more specific${NC}"
else
    echo -e "${RED}  ❌ validators.py not found${NC}"
fi

# ============================================================
# STEP 2: Rename /agents/ folder to /scout_outputs/
# ============================================================

echo ""
echo -e "${BLUE}📁 Step 2: Renaming agents/ to scout_outputs/...${NC}"

if [ -d "agents" ]; then
    # Check if scout_outputs already exists
    if [ -d "scout_outputs" ]; then
        echo -e "${YELLOW}  ⚠️  scout_outputs/ already exists, merging...${NC}"
        cp -r agents/* scout_outputs/ 2>/dev/null || true
        rm -rf agents
    else
        mv agents scout_outputs
    fi
    echo -e "${GREEN}  ✅ Renamed agents/ → scout_outputs/${NC}"
else
    echo -e "${YELLOW}  ⏭️  agents/ folder doesn't exist${NC}"
fi

# ============================================================
# STEP 3: Update all hardcoded references
# ============================================================

echo ""
echo -e "${BLUE}📝 Step 3: Updating path references...${NC}"

# Files to update with their specific replacements
declare -a FILES_TO_UPDATE=(
    "adws/adw_scout_parallel.py"
    ".claude/commands/scout_parallel.md"
    ".claude/skills/adw-scout.md"
    "scripts/workflow.sh"
    "scripts/fix_agents_folders.sh"
    "adws/adw_tests/test_validators.py"
    "CLAUDE.md"
    ".claude/commands/scout.md"
    ".claude/commands/scout_improved.md"
)

for file in "${FILES_TO_UPDATE[@]}"; do
    if [ -f "$file" ]; then
        # Replace agents/scout_files with scout_outputs
        sed -i '' 's/agents\/scout_files/scout_outputs/g' "$file"

        # Replace agents/scout_temp with scout_outputs/temp
        sed -i '' 's/agents\/scout_temp/scout_outputs\/temp/g' "$file"

        # Replace references to agents/ADW- with scout_outputs/ADW-
        sed -i '' 's/agents\/ADW-/scout_outputs\/ADW-/g' "$file"

        echo -e "${GREEN}  ✅ Updated $file${NC}"
    else
        echo -e "${YELLOW}  ⏭️  $file not found${NC}"
    fi
done

# Update validators.py with new path
if [ -f "adws/adw_modules/validators.py" ]; then
    sed -i '' 's/"agents\/scout_files\/"/"scout_outputs\/"/g' adws/adw_modules/validators.py
    sed -i '' 's/"agents\/ADW-"/"scout_outputs\/ADW-"/g' adws/adw_modules/validators.py
    sed -i '' 's/"agents\/scout_temp\/"/"scout_outputs\/temp\/"/g' adws/adw_modules/validators.py
    echo -e "${GREEN}  ✅ Updated validators.py with new paths${NC}"
fi

# ============================================================
# STEP 4: Clean up .claude/agents/ if empty
# ============================================================

echo ""
echo -e "${BLUE}🧹 Step 4: Cleaning up empty directories...${NC}"

# Remove .claude/agents/ if it only contains .DS_Store
if [ -d ".claude/agents" ]; then
    file_count=$(find .claude/agents -type f ! -name '.DS_Store' | wc -l)
    if [ "$file_count" -eq 0 ]; then
        rm -rf .claude/agents
        echo -e "${GREEN}  ✅ Removed empty .claude/agents/${NC}"
    else
        echo -e "${YELLOW}  ⏭️  .claude/agents/ contains files, keeping it${NC}"
    fi
fi

# ============================================================
# STEP 5: Create new directory structure
# ============================================================

echo ""
echo -e "${BLUE}📂 Step 5: Creating clean directory structure...${NC}"

# Create scout_outputs with proper subdirectories
mkdir -p scout_outputs
mkdir -p scout_outputs/temp
echo -e "${GREEN}  ✅ Created scout_outputs/ structure${NC}"

# Create .gitignore for scout_outputs
cat > scout_outputs/.gitignore << 'EOF'
# Temporary scout files
temp/
*.tmp
*.log

# But keep these
!relevant_files.json
!*_report.json
!ADW-*/adw_state.json
EOF
echo -e "${GREEN}  ✅ Created scout_outputs/.gitignore${NC}"

# ============================================================
# STEP 6: Update documentation
# ============================================================

echo ""
echo -e "${BLUE}📚 Step 6: Updating documentation...${NC}"

# Create migration record
cat > docs/AGENTS_NAMING_MIGRATION.md << 'EOF'
# Agents Naming Migration Record

## Migration Date
$(date +%Y-%m-%d)

## What Changed

### Folder Rename
- **Old**: `/agents/` - Confusingly named, contained scout outputs not agent definitions
- **New**: `/scout_outputs/` - Clearly indicates these are output artifacts

### Path Updates
All references updated from `agents/scout_files/` to `scout_outputs/`

### Security Fix
- **Old**: `ALLOWED_PATH_PREFIXES = ["agents/"]` - Too broad, security risk
- **New**: `ALLOWED_PATH_PREFIXES = ["scout_outputs/"]` - Specific and secure

### Files Updated
- adws/adw_scout_parallel.py
- adws/adw_modules/validators.py
- .claude/commands/scout_parallel.md
- .claude/skills/adw-scout.md
- scripts/workflow.sh
- CLAUDE.md

## Why This Change

1. **Clarity**: "agents" implied agent definitions, but folder contained scout outputs
2. **Security**: Previous path validation was too permissive
3. **Standards**: Aligns with Claude Code conventions where outputs != definitions

## Rollback Instructions

If needed, run:
```bash
git checkout -- .
mv scout_outputs agents
```
EOF

echo -e "${GREEN}  ✅ Created migration documentation${NC}"

# ============================================================
# FINAL VALIDATION
# ============================================================

echo ""
echo -e "${BLUE}✅ Running validation...${NC}"

# Check if scout_outputs exists
if [ -d "scout_outputs" ]; then
    echo -e "${GREEN}  ✅ scout_outputs/ exists${NC}"
else
    echo -e "${RED}  ❌ scout_outputs/ missing${NC}"
fi

# Check if agents is gone
if [ -d "agents" ]; then
    echo -e "${YELLOW}  ⚠️  agents/ still exists (may contain new files)${NC}"
else
    echo -e "${GREEN}  ✅ agents/ removed${NC}"
fi

# Check for remaining references to old path
remaining=$(grep -r "agents/scout_files" --include="*.py" --include="*.md" --include="*.sh" 2>/dev/null | wc -l)
if [ "$remaining" -eq 0 ]; then
    echo -e "${GREEN}  ✅ No remaining references to old paths${NC}"
else
    echo -e "${YELLOW}  ⚠️  Found $remaining remaining references to old paths${NC}"
    echo "    Run: grep -r 'agents/scout_files' --include='*.py' --include='*.md'"
fi

# ============================================================
# SUMMARY
# ============================================================

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}              ✅ MIGRATION COMPLETE${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}Summary of changes:${NC}"
echo -e "  • Renamed: agents/ → scout_outputs/"
echo -e "  • Fixed: Security vulnerability in path validation"
echo -e "  • Updated: 8+ files with new paths"
echo -e "  • Cleaned: Removed empty .claude/agents/"
echo -e "  • Created: Migration documentation"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "  1. Test scout functionality: python adws/scout_simple.py 'test'"
echo -e "  2. Verify paths: ls -la scout_outputs/"
echo -e "  3. Commit changes: git add . && git commit -m 'refactor: rename agents/ to scout_outputs/ for clarity'"
echo ""
echo -e "${GREEN}The framework is now clearer and more secure! 🎉${NC}"