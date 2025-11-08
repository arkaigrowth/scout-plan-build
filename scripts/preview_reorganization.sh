#!/bin/bash
# Documentation Reorganization Preview Script
# Purpose: Preview what will be moved without actually moving files
# Date: 2025-11-08

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}       Documentation Reorganization Preview (DRY RUN)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Count current .md files
CURRENT_COUNT=$(ls -1 *.md 2>/dev/null | wc -l)
echo -e "${YELLOW}Current state: $CURRENT_COUNT .md files in root${NC}"
echo ""

# ============================================================
# CATEGORIZE ALL FILES
# ============================================================

echo -e "${BLUE}📊 File Movement Plan:${NC}"
echo ""

# Files to stay in root
echo -e "${GREEN}✅ FILES TO KEEP IN ROOT (3):${NC}"
echo -e "  • README.md ${GRAY}(main documentation)${NC}"
echo -e "  • CLAUDE.md ${GRAY}(agent instructions)${NC}"
echo -e "  • CLAUDE.local.md ${GRAY}(local overrides)${NC}"
echo ""

# Portability documents (11 files to consolidate)
echo -e "${YELLOW}🔄 PORTABILITY DOCUMENTS TO CONSOLIDATE (11→6):${NC}"
echo -e "${GRAY}  From root:${NC}"
for file in PORTABILITY*.md PORTABLE*.md; do
    if [ -f "$file" ]; then
        size=$(wc -l < "$file")
        echo -e "  • $file ${GRAY}($size lines)${NC}"
    fi
done
echo -e "${GRAY}  Target: docs/portability/ (consolidated to 6 files)${NC}"
echo ""

# Session artifacts to archive
echo -e "${RED}📦 SESSION ARTIFACTS TO ARCHIVE (4):${NC}"
if [ -f "SESSION_CHECKPOINT.md" ]; then
    echo -e "  • SESSION_CHECKPOINT.md → ${GRAY}archive/sessions/2024-10-24-checkpoint.md${NC}"
fi
if [ -f "HANDOFF.md" ]; then
    echo -e "  • HANDOFF.md → ${GRAY}archive/sessions/2024-10-20-handoff.md${NC}"
fi
if [ -f "MCP_HOOKS_FIX_PLAN.md" ]; then
    echo -e "  • MCP_HOOKS_FIX_PLAN.md → ${GRAY}archive/plans/2024-10-25-mcp-hooks-fix.md${NC}"
fi
if [ -f "run_log.md" ]; then
    size=$(wc -l < "run_log.md")
    echo -e "  • run_log.md → ${GRAY}logs/run_log.md ($size lines)${NC}"
fi
echo ""

# Guides to organize
echo -e "${BLUE}📚 GUIDES TO ORGANIZE (6):${NC}"
if [ -f "UNINSTALL_GUIDE.md" ]; then
    echo -e "  • UNINSTALL_GUIDE.md → ${GRAY}docs/guides/deployment/${NC}"
fi
if [ -f "MCP_SETUP_GUIDE.md" ]; then
    echo -e "  • MCP_SETUP_GUIDE.md → ${GRAY}docs/guides/setup/${NC}"
fi
if [ -f "CATSY_GUIDE.md" ]; then
    echo -e "  • CATSY_GUIDE.md → ${GRAY}docs/guides/usage/${NC}"
fi
if [ -f "NAVIGATION_GUIDE.md" ]; then
    echo -e "  • NAVIGATION_GUIDE.md → ${GRAY}docs/guides/usage/${NC}"
fi
if [ -f "TECHNICAL_REFERENCE.md" ]; then
    echo -e "  • TECHNICAL_REFERENCE.md → ${GRAY}docs/reference/${NC}"
fi
if [ -f "WHERE_ARE_THE_PLANS.md" ]; then
    echo -e "  • WHERE_ARE_THE_PLANS.md → ${GRAY}UPDATE IN PLACE (navigation guide)${NC}"
fi
echo ""

# Planning documents
echo -e "${BLUE}🎯 PLANNING DOCUMENTS (3):${NC}"
if [ -f "RELEASE_READINESS.md" ]; then
    echo -e "  • RELEASE_READINESS.md → ${GRAY}docs/planning/${NC}"
fi
if [ -f "NEXT_STEPS_ACTION_PLAN.md" ]; then
    echo -e "  • NEXT_STEPS_ACTION_PLAN.md → ${GRAY}docs/planning/${NC}"
fi
if [ -f "IMPROVEMENT_STRATEGY.md" ]; then
    echo -e "  • IMPROVEMENT_STRATEGY.md → ${GRAY}docs/planning/${NC}"
fi
echo ""

# Analysis and assessments
echo -e "${BLUE}📊 ANALYSES AND ASSESSMENTS (5):${NC}"
if [ -f "AGENTS_FOLDER_ANALYSIS.md" ]; then
    echo -e "  • AGENTS_FOLDER_ANALYSIS.md → ${GRAY}ai_docs/analyses/${NC}"
fi
if [ -f "HOOKS_SKILLS_ANALYSIS.md" ]; then
    echo -e "  • HOOKS_SKILLS_ANALYSIS.md → ${GRAY}ai_docs/analyses/${NC}"
fi
if [ -f "AI_DOCS_ORGANIZATION.md" ]; then
    echo -e "  • AI_DOCS_ORGANIZATION.md → ${GRAY}ai_docs/analyses/${NC}"
fi
if [ -f "SECURITY_AUDIT_REPORT.md" ]; then
    echo -e "  • SECURITY_AUDIT_REPORT.md → ${GRAY}ai_docs/assessments/${NC}"
fi
if [ -f "PUBLIC_RELEASE_READINESS_ASSESSMENT.md" ]; then
    echo -e "  • PUBLIC_RELEASE_READINESS_ASSESSMENT.md → ${GRAY}ai_docs/assessments/${NC}"
fi
echo ""

# Project meta
echo -e "${BLUE}🗂️ PROJECT META (1):${NC}"
if [ -f "TODO.md" ]; then
    echo -e "  • TODO.md → ${GRAY}.project/${NC}"
fi
echo ""

# ============================================================
# SUMMARY
# ============================================================

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}                         SUMMARY${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Count files by destination
KEEP_COUNT=3
ARCHIVE_COUNT=0
ORGANIZE_COUNT=0

for file in *.md; do
    if [ -f "$file" ]; then
        case "$file" in
            README.md|CLAUDE.md|CLAUDE.local.md|WHERE_ARE_THE_PLANS.md)
                # Files to keep
                ;;
            SESSION_CHECKPOINT.md|HANDOFF.md|MCP_HOOKS_FIX_PLAN.md|run_log.md)
                ((ARCHIVE_COUNT++))
                ;;
            *)
                ((ORGANIZE_COUNT++))
                ;;
        esac
    fi
done

echo -e "${YELLOW}Movement Statistics:${NC}"
echo -e "  • Files to keep in root: ${GREEN}4${NC}"
echo -e "  • Files to archive: ${RED}$ARCHIVE_COUNT${NC}"
echo -e "  • Files to organize: ${BLUE}$ORGANIZE_COUNT${NC}"
echo -e "  • Portability files to consolidate: ${YELLOW}11→6${NC}"
echo ""

echo -e "${GREEN}Directory Structure to Create:${NC}"
echo -e "  docs/"
echo -e "  ├── guides/"
echo -e "  │   ├── deployment/"
echo -e "  │   ├── setup/"
echo -e "  │   └── usage/"
echo -e "  ├── reference/"
echo -e "  ├── planning/"
echo -e "  └── portability/ ${GRAY}(consolidated docs)${NC}"
echo -e ""
echo -e "  ai_docs/"
echo -e "  ├── analyses/"
echo -e "  ├── assessments/"
echo -e "  └── architecture/"
echo -e ""
echo -e "  archive/"
echo -e "  ├── sessions/"
echo -e "  ├── plans/"
echo -e "  └── portability/ ${GRAY}(redundant files)${NC}"
echo -e ""
echo -e "  .project/ ${GRAY}(can be gitignored)${NC}"
echo -e "  logs/"
echo ""

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}This is a DRY RUN preview. No files were moved.${NC}"
echo ""
echo -e "${GREEN}To execute the reorganization, run:${NC}"
echo -e "  ${BLUE}./scripts/reorganize_documentation.sh${NC}"
echo ""
echo -e "${YELLOW}Or to see just the portability consolidation:${NC}"
echo -e "  ${BLUE}ls -la PORTABILITY*.md PORTABLE*.md | wc -l${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"