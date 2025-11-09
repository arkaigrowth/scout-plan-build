#!/bin/bash

# Scout Plan Build Workflow Helper Script
# Provides deterministic operations for common tasks

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Ensure environment is set up
check_env() {
    echo -e "${BLUE}Checking environment...${NC}"

    if [ -z "$CLAUDE_CODE_MAX_OUTPUT_TOKENS" ]; then
        echo -e "${RED}Warning: CLAUDE_CODE_MAX_OUTPUT_TOKENS not set. Setting to 32768...${NC}"
        export CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768
    fi

    if [ -z "$ANTHROPIC_API_KEY" ]; then
        echo -e "${RED}Error: ANTHROPIC_API_KEY not set${NC}"
        exit 1
    fi

    echo -e "${GREEN}Environment OK${NC}"
}

# Scout for relevant files
scout() {
    local task="$1"
    echo -e "${BLUE}Scouting for: $task${NC}"

    # Create output directory
    mkdir -p scout_outputs

    # Run scout command
    echo "/scout \"$task\" \"4\""

    echo -e "${GREEN}Scout results saved to: scout_outputs/relevant_files.json${NC}"
}

# Generate plan
plan() {
    local task="$1"
    local docs="${2:-}"
    local scout_file="${3:-scout_outputs/relevant_files.json}"

    echo -e "${BLUE}Planning for: $task${NC}"

    # Create specs directory
    mkdir -p specs

    echo "/plan_w_docs \"$task\" \"$docs\" \"$scout_file\""

    echo -e "${GREEN}Plan saved to specs/${NC}"
}

# Build from plan
build() {
    local plan_file="$1"

    if [ ! -f "$plan_file" ]; then
        echo -e "${RED}Error: Plan file not found: $plan_file${NC}"
        exit 1
    fi

    echo -e "${BLUE}Building from: $plan_file${NC}"

    # Create output directories
    mkdir -p ai_docs/build_reports

    echo "/build_adw \"$plan_file\""

    echo -e "${GREEN}Build report saved to ai_docs/build_reports/${NC}"
}

# Clean up repository
cleanup() {
    echo -e "${BLUE}Cleaning up repository...${NC}"

    # Check for uncommitted changes
    if ! git diff --quiet; then
        echo -e "${RED}Warning: Uncommitted changes detected${NC}"
        git status --short
        read -p "Reset changes? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git reset --hard
            echo -e "${GREEN}Changes reset${NC}"
        fi
    else
        echo -e "${GREEN}Repository clean${NC}"
    fi
}

# Organize files
organize() {
    echo -e "${BLUE}Organizing files...${NC}"

    # Create directory structure
    mkdir -p ai_docs/{analyses,reference,architecture,build_reports,reviews}
    mkdir -p specs
    mkdir -p scout_outputs

    # Move misplaced files (if any)
    for file in ADW_*.md ARCHITECTURE_*.md COMMAND_*.md; do
        if [ -f "$file" ]; then
            echo "Moving $file to ai_docs/..."
            if [[ $file == ARCHITECTURE* ]]; then
                mv "$file" ai_docs/architecture/
            elif [[ $file == COMMAND* ]]; then
                mv "$file" ai_docs/reference/
            else
                mv "$file" ai_docs/analyses/
            fi
        fi
    done

    echo -e "${GREEN}Files organized${NC}"
}

# Show status
status() {
    echo -e "${BLUE}Repository Status${NC}"
    echo "=================="

    echo -e "\n${BLUE}Git Status:${NC}"
    git status --short || echo "Not a git repository"

    echo -e "\n${BLUE}Recent Analyses:${NC}"
    ls -lt ai_docs/analyses/ 2>/dev/null | head -5 || echo "No analyses found"

    echo -e "\n${BLUE}Recent Plans:${NC}"
    ls -lt specs/ 2>/dev/null | head -5 || echo "No plans found"

    echo -e "\n${BLUE}TODO Items:${NC}"
    head -20 TODO.md 2>/dev/null || echo "No TODO.md found"
}

# Main command handler
case "${1:-help}" in
    check)
        check_env
        ;;
    scout)
        check_env
        scout "$2"
        ;;
    plan)
        check_env
        plan "$2" "$3" "$4"
        ;;
    build)
        check_env
        build "$2"
        ;;
    cleanup)
        cleanup
        ;;
    organize)
        organize
        ;;
    status)
        status
        ;;
    workflow)
        # Full workflow
        check_env
        scout "$2"
        plan "$2" "$3"
        echo -e "${BLUE}Ready to build. Run: ./scripts/workflow.sh build specs/[plan-file].md${NC}"
        ;;
    help|*)
        echo "Scout Plan Build Workflow Helper"
        echo "================================"
        echo ""
        echo "Usage: $0 <command> [arguments]"
        echo ""
        echo "Commands:"
        echo "  check              - Check environment setup"
        echo "  scout <task>       - Scout for relevant files"
        echo "  plan <task> [docs] - Generate implementation plan"
        echo "  build <plan>       - Build from plan file"
        echo "  cleanup            - Clean up repository"
        echo "  organize           - Organize files into proper directories"
        echo "  status             - Show repository status"
        echo "  workflow <task>    - Run scout + plan workflow"
        echo "  help               - Show this help"
        echo ""
        echo "Examples:"
        echo "  $0 scout \"Add authentication\""
        echo "  $0 plan \"Add authentication\" \"https://docs.auth.com\""
        echo "  $0 build specs/auth-plan.md"
        echo "  $0 workflow \"Add authentication\""
        ;;
esac