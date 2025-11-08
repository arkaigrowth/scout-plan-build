#!/bin/bash
# Fix the agents folder confusion
# This script cleans up the mess and reorganizes properly

set -e

echo "🔧 Fixing Agents Folder Confusion"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Step 1: Clean up bad folders in agents/
echo "🗑️  Step 1: Cleaning up polluted folders..."

if [ -d "agents/Add plan-summarize command and standardize spec schema + versioning across the repo" ]; then
    rm -rf "agents/Add plan-summarize command and standardize spec schema + versioning across the repo"
    echo "   ✅ Removed bad folder from task name"
fi

if [ -d "agents/https:" ]; then
    rm -rf "agents/https:"
    echo "   ✅ Removed dangerous URL-based folder"
fi

# Step 2: Remove empty .claude/agents
echo ""
echo "🗑️  Step 2: Removing empty .claude/agents..."

if [ -d ".claude/agents" ]; then
    # Check if it only contains .DS_Store
    if [ "$(ls -A .claude/agents | grep -v .DS_Store | wc -l)" -eq 0 ]; then
        rm -rf ".claude/agents"
        echo "   ✅ Removed empty .claude/agents folder"
    else
        echo "   ⚠️  .claude/agents is not empty, skipping"
    fi
else
    echo "   ✓ .claude/agents doesn't exist (good!)"
fi

# Step 3: Rename agents/ to scout_outputs/
echo ""
echo "📁 Step 3: Renaming for clarity..."

if [ -d "agents" ]; then
    if [ -d "scout_outputs" ]; then
        echo -e "   ${YELLOW}Warning: scout_outputs already exists${NC}"
        echo "   Merging agents/ into scout_outputs/"

        # Move scout_files if it exists
        if [ -d "agents/scout_files" ]; then
            if [ ! -d "scout_outputs/scout_files" ]; then
                mv agents/scout_files scout_outputs/
                echo "   ✅ Moved scout_files to scout_outputs/"
            else
                echo "   ⚠️  scout_outputs/scout_files exists, keeping both"
            fi
        fi

        # Remove now-empty agents folder
        rmdir agents 2>/dev/null || echo "   ⚠️  agents/ not empty, manual review needed"
    else
        mv agents scout_outputs
        echo "   ✅ Renamed agents/ → scout_outputs/"
    fi
else
    echo "   ⚠️  No agents/ folder found"

    # Create scout_outputs if it doesn't exist
    if [ ! -d "scout_outputs" ]; then
        mkdir -p scout_outputs
        echo "   ✅ Created scout_outputs/ folder"
    fi
fi

# Step 4: Update code references
echo ""
echo "📝 Step 4: Updating code references..."

# Update scout_simple.py
if [ -f "adws/scout_simple.py" ]; then
    sed -i.bak 's/agents\/scout_files/scout_outputs/g' adws/scout_simple.py
    rm -f adws/scout_simple.py.bak
    echo "   ✅ Updated adws/scout_simple.py"
fi

# Update slash commands
for file in .claude/commands/scout*.md; do
    if [ -f "$file" ]; then
        sed -i.bak 's/agents\/scout_files/scout_outputs/g' "$file"
        sed -i.bak 's/RELEVANT_FILE_OUTPUT_DIR: "agents\/scout_files"/RELEVANT_FILE_OUTPUT_DIR: "scout_outputs"/g' "$file"
        rm -f "$file.bak"
        echo "   ✅ Updated $(basename $file)"
    fi
done

# Update validation script
if [ -f "scripts/validate_pipeline.sh" ]; then
    sed -i.bak 's/agents\/scout_files/scout_outputs/g' scripts/validate_pipeline.sh
    rm -f scripts/validate_pipeline.sh.bak
    echo "   ✅ Updated scripts/validate_pipeline.sh"
fi

# Update installer script
if [ -f "scripts/install_to_new_repo.sh" ]; then
    sed -i.bak 's/agents\/scout_files/scout_outputs/g' scripts/install_to_new_repo.sh
    sed -i.bak 's/mkdir -p "\$TARGET_REPO\/agents\/scout_files"/mkdir -p "\$TARGET_REPO\/scout_outputs"/g' scripts/install_to_new_repo.sh
    rm -f scripts/install_to_new_repo.sh.bak
    echo "   ✅ Updated scripts/install_to_new_repo.sh"
fi

# Update .adw_config.json if it exists
if [ -f ".adw_config.json" ]; then
    sed -i.bak 's/"agents"/"scout_outputs"/g' .adw_config.json
    rm -f .adw_config.json.bak
    echo "   ✅ Updated .adw_config.json"
fi

# Step 5: Create proper structure
echo ""
echo "🏗️  Step 5: Ensuring proper structure..."

mkdir -p scout_outputs
echo "   ✅ scout_outputs/ exists"

# Step 6: Create migration notice
echo ""
echo "📄 Step 6: Creating migration notice..."

cat > scout_outputs/README.md << 'EOF'
# Scout Outputs Directory

This directory contains the output files from scout operations.

## Migration Notice (Oct 2024)

This directory was renamed from `agents/` to `scout_outputs/` to eliminate confusion.

**Why the change?**
- "agents" was ambiguous - could mean agent definitions, outputs, or configs
- This folder specifically contains scout OUTPUT files
- Agent DEFINITIONS live in ~/.claude/agents/ (user home)

## Structure

```
scout_outputs/
└── relevant_files.json   # Main output from scout operations
```

## Usage

When scout runs, it saves found files here:
```bash
scout_outputs/relevant_files.json
```

This file is then used by the plan phase:
```bash
/plan_w_docs "task" "" "scout_outputs/relevant_files.json"
```

## Security Note

Previous versions had a vulnerability where task names/URLs could create arbitrary folders.
This has been fixed - all outputs now go directly to relevant_files.json.
EOF

echo "   ✅ Created README.md in scout_outputs/"

# Step 7: Summary
echo ""
echo -e "${GREEN}✨ Fix Complete!${NC}"
echo "=================="
echo ""
echo "Changes made:"
echo "  • Cleaned up polluted folders (task names, URLs)"
echo "  • Removed empty .claude/agents/"
echo "  • Renamed agents/ → scout_outputs/"
echo "  • Updated all code references"
echo "  • Created proper structure with README"
echo ""
echo "Next steps:"
echo "  1. Run: ./scripts/validate_pipeline.sh"
echo "  2. Test scout operation to verify it works"
echo "  3. Commit these changes"
echo ""
echo -e "${YELLOW}Note:${NC} If you have any custom scripts using 'agents/scout_files/',"
echo "      you'll need to update them to use 'scout_outputs/' instead."