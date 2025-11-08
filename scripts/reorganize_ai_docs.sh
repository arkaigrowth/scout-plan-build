#!/bin/bash
# Reorganize scout_outputs into ai_docs for better structure
# Following the principle: AI-generated artifacts belong in ai_docs/

set -e

echo "📁 Reorganizing AI-Generated Artifacts"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Step 1: Create proper ai_docs structure
echo "🏗️  Step 1: Creating organized ai_docs structure..."

mkdir -p ai_docs/scout
mkdir -p ai_docs/build_reports
mkdir -p ai_docs/analyses
mkdir -p ai_docs/reviews
mkdir -p ai_docs/architecture
mkdir -p ai_docs/reference

echo "   ✅ Created ai_docs subdirectories"

# Step 2: Move scout_outputs to ai_docs/scout
echo ""
echo "📦 Step 2: Moving scout_outputs → ai_docs/scout..."

if [ -d "scout_outputs" ]; then
    # Move the files, not the directory itself
    if [ -f "scout_outputs/relevant_files.json" ]; then
        mv scout_outputs/relevant_files.json ai_docs/scout/
        echo "   ✅ Moved relevant_files.json"
    fi

    if [ -f "scout_outputs/README.md" ]; then
        mv scout_outputs/README.md ai_docs/scout/
        echo "   ✅ Moved README.md"
    fi

    # Check for scout_files subdirectory
    if [ -d "scout_outputs/scout_files" ]; then
        # Move any files from scout_files up to scout/
        if [ -f "scout_outputs/scout_files/relevant_files.json" ]; then
            mv scout_outputs/scout_files/relevant_files.json ai_docs/scout/relevant_files_backup.json
            echo "   ✅ Moved backup relevant_files.json"
        fi
        rmdir scout_outputs/scout_files 2>/dev/null || true
    fi

    # Remove now-empty scout_outputs
    rmdir scout_outputs 2>/dev/null || echo "   ⚠️  scout_outputs not empty, manual review needed"
else
    echo "   ⚠️  No scout_outputs folder found"
fi

# Step 3: Update all code references
echo ""
echo "📝 Step 3: Updating code references..."

# Update scout_simple.py
if [ -f "adws/scout_simple.py" ]; then
    sed -i.bak 's|scout_outputs|ai_docs/scout|g' adws/scout_simple.py
    rm -f adws/scout_simple.py.bak
    echo "   ✅ Updated adws/scout_simple.py"
fi

# Update slash commands
for file in .claude/commands/scout*.md .claude/commands/plan*.md .claude/commands/build*.md; do
    if [ -f "$file" ]; then
        sed -i.bak 's|scout_outputs/relevant_files\.json|ai_docs/scout/relevant_files.json|g' "$file"
        sed -i.bak 's|scout_outputs|ai_docs/scout|g' "$file"
        sed -i.bak 's|RELEVANT_FILE_OUTPUT_DIR: "scout_outputs"|RELEVANT_FILE_OUTPUT_DIR: "ai_docs/scout"|g' "$file"
        rm -f "$file.bak"
        echo "   ✅ Updated $(basename $file)"
    fi
done

# Update validation script
if [ -f "scripts/validate_pipeline.sh" ]; then
    sed -i.bak 's|scout_outputs/relevant_files\.json|ai_docs/scout/relevant_files.json|g' scripts/validate_pipeline.sh
    sed -i.bak 's|scout_outputs|ai_docs/scout|g' scripts/validate_pipeline.sh
    rm -f scripts/validate_pipeline.sh.bak
    echo "   ✅ Updated scripts/validate_pipeline.sh"
fi

# Update installer script
if [ -f "scripts/install_to_new_repo.sh" ]; then
    sed -i.bak 's|mkdir -p "\$TARGET_REPO/scout_outputs"|mkdir -p "\$TARGET_REPO/ai_docs/scout"|g' scripts/install_to_new_repo.sh
    sed -i.bak 's|scout_outputs/relevant_files\.json|ai_docs/scout/relevant_files.json|g' scripts/install_to_new_repo.sh
    sed -i.bak 's|scout_outputs|ai_docs/scout|g' scripts/install_to_new_repo.sh
    rm -f scripts/install_to_new_repo.sh.bak
    echo "   ✅ Updated scripts/install_to_new_repo.sh"
fi

# Update documentation
for doc in PORTABLE_DEPLOYMENT_GUIDE.md SESSION_CHECKPOINT.md CLAUDE.md; do
    if [ -f "$doc" ]; then
        sed -i.bak 's|scout_outputs/relevant_files\.json|ai_docs/scout/relevant_files.json|g' "$doc"
        sed -i.bak 's|scout_outputs|ai_docs/scout|g' "$doc"
        rm -f "$doc.bak"
        echo "   ✅ Updated $doc"
    fi
done

# Update .adw_config.json if it exists
if [ -f ".adw_config.json" ]; then
    sed -i.bak 's|"scout_outputs"|"ai_docs/scout"|g' .adw_config.json
    rm -f .adw_config.json.bak
    echo "   ✅ Updated .adw_config.json"
fi

# Step 4: Create structure documentation
echo ""
echo "📄 Step 4: Creating structure documentation..."

cat > ai_docs/README.md << 'EOF'
# AI-Generated Documentation Structure

All AI-generated artifacts are organized here for clarity and consistency.

## Directory Structure

```
ai_docs/
├── scout/              # Scout exploration outputs
│   └── relevant_files.json
├── build_reports/      # Build phase reports
├── analyses/           # System analyses
├── reviews/            # Code reviews
├── architecture/       # Architecture documentation
└── reference/          # Reference guides
```

## Workflow Outputs

1. **Scout Phase** → `ai_docs/scout/relevant_files.json`
2. **Plan Phase** → `specs/` (separate top-level for visibility)
3. **Build Phase** → `ai_docs/build_reports/`

## Why This Organization?

- **Consistency**: All AI outputs in one place
- **Clarity**: Clear separation from human-written code
- **Discoverability**: Easy to find all AI artifacts
- **Gitignore-friendly**: Can exclude all AI outputs with one pattern

## Usage

```bash
# Scout saves to:
ai_docs/scout/relevant_files.json

# Plan reads from scout and saves to:
specs/issue-XXX-*.md

# Build reads spec and saves to:
ai_docs/build_reports/*-report.md
```
EOF

echo "   ✅ Created ai_docs/README.md"

# Step 5: Summary
echo ""
echo -e "${GREEN}✨ Reorganization Complete!${NC}"
echo "=========================="
echo ""
echo "New structure:"
echo "  ai_docs/"
echo "  ├── scout/           # Scout outputs (moved from scout_outputs/)"
echo "  ├── build_reports/   # Build reports (existing)"
echo "  ├── analyses/        # Analysis docs (existing)"
echo "  ├── reviews/         # Reviews (new)"
echo "  ├── architecture/    # Architecture docs (existing)"
echo "  └── reference/       # Reference guides (existing)"
echo ""
echo "Benefits:"
echo "  • All AI-generated content in one place"
echo "  • Clear organizational principle"
echo "  • Better for .gitignore patterns"
echo "  • Easier to understand for new developers"
echo ""
echo -e "${YELLOW}Next step:${NC} Run ./scripts/validate_pipeline.sh to verify everything works"