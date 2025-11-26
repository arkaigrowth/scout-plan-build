#!/usr/bin/env bash
#
# Scout-Plan-Build Framework Installer
# =====================================
#
# One-liner installation:
#   curl -sL https://raw.githubusercontent.com/arkaigrowth/scout-plan-build/main/install.sh | bash -s /path/to/target
#
# With options:
#   curl -sL URL | bash -s -- /path/to/target --minimal
#   curl -sL URL | bash -s -- /path/to/target --full
#   curl -sL URL | bash -s -- /path/to/target --dry-run
#   curl -sL URL | bash -s -- --help
#
# Version: 1.0.0
# License: MIT
# Repository: https://github.com/arkaigrowth/scout-plan-build
#

set -euo pipefail

# =============================================================================
# Configuration
# =============================================================================

readonly VERSION="1.0.0"
readonly REPO_URL="https://github.com/arkaigrowth/scout-plan-build"
readonly REPO_NAME="arkaigrowth/scout-plan-build"
readonly MIN_BASH_VERSION=4
readonly MIN_PYTHON_VERSION="3.10"
readonly TEMP_DIR="${TMPDIR:-/tmp}/spb-install-$$"

# Installation modes
MODE_MINIMAL="minimal"
MODE_FULL="full"
DEFAULT_MODE="$MODE_MINIMAL"

# =============================================================================
# Colors and Output Helpers
# =============================================================================

# Check if stdout is a terminal for color support
if [[ -t 1 ]]; then
    readonly RED='\033[0;31m'
    readonly GREEN='\033[0;32m'
    readonly YELLOW='\033[1;33m'
    readonly BLUE='\033[0;34m'
    readonly CYAN='\033[0;36m'
    readonly BOLD='\033[1m'
    readonly DIM='\033[2m'
    readonly NC='\033[0m'
else
    readonly RED=''
    readonly GREEN=''
    readonly YELLOW=''
    readonly BLUE=''
    readonly CYAN=''
    readonly BOLD=''
    readonly DIM=''
    readonly NC=''
fi

# Output functions
info() { echo -e "${BLUE}[INFO]${NC} $*"; }
success() { echo -e "${GREEN}[OK]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }
step() { echo -e "  ${GREEN}✓${NC} $*"; }
step_pending() { echo -e "  ${DIM}○${NC} $*"; }

header() {
    echo ""
    echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}  $*${NC}"
    echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# =============================================================================
# Cleanup Handler
# =============================================================================

cleanup() {
    local exit_code=$?
    if [[ -d "$TEMP_DIR" ]]; then
        rm -rf "$TEMP_DIR"
    fi
    if [[ $exit_code -ne 0 ]]; then
        echo ""
        error "Installation failed. Check the errors above."
        echo ""
        echo "For help, visit: ${REPO_URL}/issues"
    fi
    exit $exit_code
}

trap cleanup EXIT INT TERM

# =============================================================================
# Help and Usage
# =============================================================================

show_help() {
    cat << EOF
${BOLD}Scout-Plan-Build Framework Installer v${VERSION}${NC}

${BOLD}USAGE:${NC}
    curl -sL ${REPO_URL}/raw/main/install.sh | bash -s [TARGET] [OPTIONS]

    # Or if downloaded locally:
    ./install.sh [TARGET] [OPTIONS]

${BOLD}ARGUMENTS:${NC}
    TARGET              Target directory for installation (required)
                        Must be an existing, writable directory

${BOLD}OPTIONS:${NC}
    --minimal           Install slash commands only (default, quick eval)
    --full              Install everything (commands, modules, hooks, skills)
    --dry-run           Show what would be installed without making changes
    --force             Overwrite existing installation without prompting
    --help, -h          Show this help message

${BOLD}EXAMPLES:${NC}
    # Basic installation to current project
    curl -sL ${REPO_URL}/raw/main/install.sh | bash -s ./my-project

    # Full installation with all features
    curl -sL ${REPO_URL}/raw/main/install.sh | bash -s -- ./my-project --full

    # Preview what would be installed
    curl -sL ${REPO_URL}/raw/main/install.sh | bash -s -- ./my-project --dry-run

${BOLD}INSTALLATION MODES:${NC}
    ${GREEN}--minimal (default)${NC}
        - .claude/commands/ (slash commands)
        - .adw_config.json
        - .env.template
        - Basic CLAUDE.md
        Best for: Quick evaluation, small projects

    ${GREEN}--full${NC}
        - Everything from --minimal
        - adws/ (Python workflow modules)
        - .claude/hooks/ (event hooks)
        - .claude/skills/ (workflow skills)
        - scripts/ (utility scripts)
        Best for: Full adoption, CI/CD integration

${BOLD}REQUIREMENTS:${NC}
    - Bash >= 4.0
    - Git >= 2.0
    - Python >= 3.10

${BOLD}MORE INFO:${NC}
    Repository: ${REPO_URL}
    Issues:     ${REPO_URL}/issues

EOF
    exit 0
}

# =============================================================================
# Pre-flight Checks
# =============================================================================

check_bash_version() {
    local bash_version="${BASH_VERSINFO[0]}"
    if [[ "$bash_version" -lt "$MIN_BASH_VERSION" ]]; then
        error "Bash version $MIN_BASH_VERSION or higher required (found: $BASH_VERSION)"
        echo ""
        echo "Upgrade bash:"
        echo "  macOS: brew install bash"
        echo "  Linux: sudo apt-get install bash"
        return 1
    fi
    step "Bash ${BASH_VERSION}"
}

check_git() {
    if ! command -v git &> /dev/null; then
        error "Git is required but not installed"
        echo ""
        echo "Install git:"
        echo "  macOS: xcode-select --install"
        echo "  Linux: sudo apt-get install git"
        return 1
    fi
    local git_version
    git_version=$(git --version | awk '{print $3}')
    step "Git ${git_version}"
}

check_python() {
    local python_cmd=""
    local python_version=""

    # Try python3 first, then python
    for cmd in python3 python; do
        if command -v "$cmd" &> /dev/null; then
            python_version=$("$cmd" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")')
            python_cmd="$cmd"
            break
        fi
    done

    if [[ -z "$python_cmd" ]]; then
        error "Python ${MIN_PYTHON_VERSION}+ is required but not found"
        echo ""
        echo "Install Python:"
        echo "  macOS: brew install python@3.11"
        echo "  Linux: sudo apt-get install python3"
        return 1
    fi

    # Check version
    local major minor
    major=$("$python_cmd" -c 'import sys; print(sys.version_info.major)')
    minor=$("$python_cmd" -c 'import sys; print(sys.version_info.minor)')

    if [[ "$major" -lt 3 ]] || { [[ "$major" -eq 3 ]] && [[ "$minor" -lt 10 ]]; }; then
        error "Python ${MIN_PYTHON_VERSION}+ required (found: ${python_version})"
        return 1
    fi

    step "Python ${python_version}"
}

check_target_directory() {
    local target="$1"

    # Check if directory exists
    if [[ ! -d "$target" ]]; then
        error "Target directory does not exist: $target"
        echo ""
        echo "Create it first:"
        echo "  mkdir -p $target"
        return 1
    fi

    # Check if writable
    if [[ ! -w "$target" ]]; then
        error "Target directory is not writable: $target"
        return 1
    fi

    step "Target directory exists and is writable"
}

check_existing_installation() {
    local target="$1"
    local force="$2"

    if [[ -f "$target/.adw_config.json" ]]; then
        if [[ "$force" == "true" ]]; then
            warn "Existing installation found - will upgrade"
            # Backup existing config
            if [[ -f "$target/.adw_config.json" ]]; then
                cp "$target/.adw_config.json" "$target/.adw_config.json.backup"
                step "Backed up .adw_config.json"
            fi
        else
            warn "Existing installation detected at $target"
            echo ""
            echo "Options:"
            echo "  1. Re-run with --force to upgrade"
            echo "  2. Choose a different target directory"
            echo ""
            read -r -p "Upgrade existing installation? [y/N] " response
            if [[ ! "$response" =~ ^[Yy]$ ]]; then
                error "Installation cancelled by user"
                return 1
            fi
            # Backup
            if [[ -f "$target/.adw_config.json" ]]; then
                cp "$target/.adw_config.json" "$target/.adw_config.json.backup"
                step "Backed up .adw_config.json"
            fi
        fi
    fi
}

run_preflight_checks() {
    local target="$1"
    local force="$2"

    header "Pre-flight Checks"
    echo ""

    check_bash_version || return 1
    check_git || return 1
    check_python || return 1
    check_target_directory "$target" || return 1
    check_existing_installation "$target" "$force" || return 1

    echo ""
    success "All pre-flight checks passed"
}

# =============================================================================
# Download Functions
# =============================================================================

download_with_sparse_checkout() {
    info "Downloading framework (sparse checkout)..."

    mkdir -p "$TEMP_DIR"
    cd "$TEMP_DIR"

    # Try sparse checkout first (most efficient)
    if git clone --depth 1 --filter=blob:none --sparse "$REPO_URL.git" repo 2>/dev/null; then
        cd repo
        git sparse-checkout set adws .claude scripts .scout_framework.yaml 2>/dev/null || true
        step "Downloaded via sparse checkout"
        return 0
    fi

    return 1
}

download_with_tarball() {
    info "Downloading framework (tarball fallback)..."

    mkdir -p "$TEMP_DIR"
    cd "$TEMP_DIR"

    local tarball_url="${REPO_URL}/archive/refs/heads/main.tar.gz"

    if command -v curl &> /dev/null; then
        curl -sL "$tarball_url" | tar -xz
    elif command -v wget &> /dev/null; then
        wget -qO- "$tarball_url" | tar -xz
    else
        error "Neither curl nor wget available for download"
        return 1
    fi

    # Rename extracted directory
    mv scout-plan-build-main repo
    step "Downloaded via tarball"
    return 0
}

download_framework() {
    header "Downloading Framework"
    echo ""

    # Try sparse checkout first, fall back to tarball
    if ! download_with_sparse_checkout; then
        if ! download_with_tarball; then
            error "Failed to download framework"
            return 1
        fi
    fi

    echo ""
    success "Framework downloaded successfully"
}

# =============================================================================
# Installation Functions
# =============================================================================

create_directories() {
    local target="$1"
    local dry_run="$2"

    local dirs=(
        "specs"
        "scout_outputs"
        "scout_outputs/temp"
        "scout_outputs/workflows"
        "ai_docs/build_reports"
        "ai_docs/reviews"
        "ai_docs/research"
        "ai_docs/research/videos"
        "ai_docs/research/articles"
        "ai_docs/research/implementations"
        "ai_docs/outputs"
        ".claude/commands"
        ".claude/memory"
        ".claude/state"
    )

    for dir in "${dirs[@]}"; do
        if [[ "$dry_run" == "true" ]]; then
            step_pending "Would create: $target/$dir"
        else
            mkdir -p "$target/$dir"
            # Add .gitkeep to empty directories
            if [[ ! -f "$target/$dir/.gitkeep" ]]; then
                touch "$target/$dir/.gitkeep"
            fi
        fi
    done

    if [[ "$dry_run" != "true" ]]; then
        step "Created directory structure"
    fi
}

install_minimal() {
    local source="$1"
    local target="$2"
    local dry_run="$3"

    info "Installing minimal components..."

    # Slash commands
    local commands=(
        "plan_w_docs.md"
        "plan_w_docs_improved.md"
        "build_adw.md"
        "build.md"
        "scout.md"
        "scout_improved.md"
        "scout_fixed.md"
        "init-framework.md"
    )

    for cmd in "${commands[@]}"; do
        if [[ -f "$source/.claude/commands/$cmd" ]]; then
            if [[ "$dry_run" == "true" ]]; then
                step_pending "Would copy: .claude/commands/$cmd"
            else
                cp "$source/.claude/commands/$cmd" "$target/.claude/commands/"
            fi
        fi
    done

    if [[ "$dry_run" != "true" ]]; then
        step "Installed slash commands"
    fi
}

install_full() {
    local source="$1"
    local target="$2"
    local dry_run="$3"

    # First do minimal install
    install_minimal "$source" "$target" "$dry_run"

    info "Installing full components..."

    # Additional commands
    local extra_commands=(
        "init-parallel-worktrees.md"
        "compare-worktrees.md"
        "merge-worktree.md"
        "scout_parallel.md"
    )

    for cmd in "${extra_commands[@]}"; do
        if [[ -f "$source/.claude/commands/$cmd" ]]; then
            if [[ "$dry_run" == "true" ]]; then
                step_pending "Would copy: .claude/commands/$cmd"
            else
                cp "$source/.claude/commands/$cmd" "$target/.claude/commands/"
            fi
        fi
    done

    # Core modules (adws/)
    if [[ -d "$source/adws" ]]; then
        if [[ "$dry_run" == "true" ]]; then
            step_pending "Would copy: adws/ (Python modules)"
        else
            cp -r "$source/adws" "$target/"
            step "Installed Python modules (adws/)"
        fi
    fi

    # Hooks
    if [[ -d "$source/.claude/hooks" ]]; then
        if [[ "$dry_run" == "true" ]]; then
            step_pending "Would copy: .claude/hooks/"
        else
            cp -r "$source/.claude/hooks" "$target/.claude/"
            step "Installed hooks"
        fi
    fi

    # Skills
    if [[ -d "$source/.claude/skills" ]]; then
        if [[ "$dry_run" == "true" ]]; then
            step_pending "Would copy: .claude/skills/"
        else
            cp -r "$source/.claude/skills" "$target/.claude/"
            step "Installed skills"
        fi
    fi

    # Scripts
    if [[ -d "$source/scripts" ]]; then
        if [[ "$dry_run" == "true" ]]; then
            step_pending "Would copy: scripts/"
        else
            mkdir -p "$target/scripts"
            cp "$source/scripts/"*.sh "$target/scripts/" 2>/dev/null || true
            chmod +x "$target/scripts/"*.sh 2>/dev/null || true
            step "Installed utility scripts"
        fi
    fi
}

generate_env_template() {
    local target="$1"
    local dry_run="$2"

    if [[ "$dry_run" == "true" ]]; then
        step_pending "Would create: .env.template"
        return
    fi

    cat > "$target/.env.template" << 'EOF'
# Scout-Plan-Build Configuration
# ==============================
# Copy to .env and fill in your values:
#   cp .env.template .env
#   # Edit .env with your values
#   export $(grep -v '^#' .env | xargs)

# Required - Claude API Key
ANTHROPIC_API_KEY=sk-ant-...

# Required - Prevents token limit errors
CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768

# Optional - GitHub Integration
GITHUB_PAT=ghp_...
GITHUB_REPO_URL=https://github.com/owner/repo

# Optional - Additional Services
E2B_API_KEY=
R2_ACCOUNT_ID=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_NAME=
EOF

    step "Created .env.template"
}

generate_config() {
    local target="$1"
    local dry_run="$2"

    if [[ "$dry_run" == "true" ]]; then
        step_pending "Would create: .adw_config.json"
        return
    fi

    local repo_name
    repo_name=$(basename "$target")

    cat > "$target/.adw_config.json" << EOF
{
  "project": {
    "name": "${repo_name}",
    "type": "auto-detect"
  },
  "paths": {
    "specs": "specs/",
    "scout_outputs": "scout_outputs/",
    "ai_docs": "ai_docs/",
    "app_code": ".",
    "allowed": ["specs", "scout_outputs", "ai_docs", "app", "src", "lib"]
  },
  "workflow": {
    "use_github": true,
    "auto_branch": true,
    "branch_prefix": "feature/"
  }
}
EOF

    step "Created .adw_config.json"
}

generate_claude_md() {
    local target="$1"
    local mode="$2"
    local dry_run="$3"

    if [[ -f "$target/CLAUDE.md" ]]; then
        if [[ "$dry_run" == "true" ]]; then
            step_pending "Would skip: CLAUDE.md (already exists)"
        else
            step "Skipped CLAUDE.md (already exists)"
        fi
        return
    fi

    if [[ "$dry_run" == "true" ]]; then
        step_pending "Would create: CLAUDE.md"
        return
    fi

    cat > "$target/CLAUDE.md" << 'EOF'
# Scout-Plan-Build Workflow

## Quick Start

### 1. Setup Environment
```bash
cp .env.template .env
# Edit .env with your API keys
export $(grep -v '^#' .env | xargs)
```

### 2. Basic Workflow

```bash
# Find relevant files for your task
/scout "implement user authentication"

# Create a plan/spec
/plan_w_docs_improved "implement user auth" "" "scout_outputs/relevant_files.json"

# Build from the spec
/build_adw "specs/issue-001-*.md"
```

## Command Reference

| Command | Purpose | Usage |
|---------|---------|-------|
| `/scout` | Find relevant files | `/scout "task description"` |
| `/plan_w_docs_improved` | Create spec | `/plan_w_docs_improved "task" "docs" "files.json"` |
| `/build_adw` | Build from spec | `/build_adw "specs/plan.md"` |

## Directory Structure

```
specs/              # Implementation plans
scout_outputs/      # Scout discovery results
ai_docs/            # AI-generated documentation
  build_reports/    # Build execution reports
  reviews/          # Code review reports
.claude/
  commands/         # Slash commands
  memory/           # Workflow memory
  state/            # State persistence
```

## Configuration

Edit `.adw_config.json` to customize:
- Directory names and paths
- Git workflow behavior
- Allowed modification paths

## More Information

Repository: https://github.com/arkaigrowth/scout-plan-build
EOF

    step "Created CLAUDE.md"
}

generate_install_info() {
    local target="$1"
    local mode="$2"
    local dry_run="$3"

    if [[ "$dry_run" == "true" ]]; then
        step_pending "Would create: .scout_install_info.json"
        return
    fi

    local install_date
    install_date=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    cat > "$target/.scout_install_info.json" << EOF
{
  "installer_version": "${VERSION}",
  "install_date": "${install_date}",
  "install_mode": "${mode}",
  "source_repo": "${REPO_URL}",
  "target_path": "${target}"
}
EOF

    step "Created .scout_install_info.json"
}

run_installation() {
    local target="$1"
    local mode="$2"
    local dry_run="$3"

    local source="$TEMP_DIR/repo"

    header "Installing Framework"
    echo ""
    info "Mode: ${BOLD}${mode}${NC}"
    info "Target: ${BOLD}${target}${NC}"
    if [[ "$dry_run" == "true" ]]; then
        warn "DRY RUN - No changes will be made"
    fi
    echo ""

    # Create directories
    create_directories "$target" "$dry_run"

    # Install based on mode
    if [[ "$mode" == "$MODE_FULL" ]]; then
        install_full "$source" "$target" "$dry_run"
    else
        install_minimal "$source" "$target" "$dry_run"
    fi

    # Generate configuration files
    generate_env_template "$target" "$dry_run"
    generate_config "$target" "$dry_run"
    generate_claude_md "$target" "$mode" "$dry_run"
    generate_install_info "$target" "$mode" "$dry_run"

    echo ""
    if [[ "$dry_run" == "true" ]]; then
        success "Dry run complete - no changes made"
    else
        success "Installation complete"
    fi
}

# =============================================================================
# Post-installation
# =============================================================================

show_next_steps() {
    local target="$1"
    local mode="$2"

    header "Next Steps"
    echo ""
    echo "  1. Navigate to your project:"
    echo "     ${CYAN}cd $target${NC}"
    echo ""
    echo "  2. Configure environment variables:"
    echo "     ${CYAN}cp .env.template .env${NC}"
    echo "     ${CYAN}# Edit .env with your API keys${NC}"
    echo "     ${CYAN}export \$(grep -v '^#' .env | xargs)${NC}"
    echo ""
    echo "  3. Start using the framework:"
    echo "     ${CYAN}/scout \"your task description\"${NC}"
    echo "     ${CYAN}/plan_w_docs_improved \"task\" \"\" \"scout_outputs/relevant_files.json\"${NC}"
    echo "     ${CYAN}/build_adw \"specs/your-plan.md\"${NC}"
    echo ""

    if [[ "$mode" == "$MODE_FULL" ]]; then
        echo "  4. Validate installation:"
        echo "     ${CYAN}./scripts/validate_pipeline.sh${NC}"
        echo ""
    fi

    echo "  Documentation: ${CYAN}${REPO_URL}${NC}"
    echo ""
}

# =============================================================================
# Main Entry Point
# =============================================================================

main() {
    local target=""
    local mode="$DEFAULT_MODE"
    local dry_run="false"
    local force="false"

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --help|-h)
                show_help
                ;;
            --minimal)
                mode="$MODE_MINIMAL"
                shift
                ;;
            --full)
                mode="$MODE_FULL"
                shift
                ;;
            --dry-run)
                dry_run="true"
                shift
                ;;
            --force)
                force="true"
                shift
                ;;
            --)
                shift
                ;;
            -*)
                error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
            *)
                if [[ -z "$target" ]]; then
                    target="$1"
                else
                    error "Multiple targets specified"
                    exit 1
                fi
                shift
                ;;
        esac
    done

    # Check target is specified
    if [[ -z "$target" ]]; then
        error "Target directory is required"
        echo ""
        echo "Usage: curl -sL ${REPO_URL}/raw/main/install.sh | bash -s /path/to/target"
        echo "       Use --help for more options"
        exit 1
    fi

    # Convert to absolute path
    target=$(cd "$target" 2>/dev/null && pwd)

    # Show banner
    echo ""
    echo -e "${BOLD}${CYAN}"
    echo "  ____                  _     ____  _               ____        _ _     _ "
    echo " / ___|  ___ ___  _   _| |_  |  _ \\| | __ _ _ __   | __ ) _   _(_) | __| |"
    echo " \\___ \\ / __/ _ \\| | | | __| | |_) | |/ _\` | '_ \\  |  _ \\| | | | | |/ _\` |"
    echo "  ___) | (_| (_) | |_| | |_  |  __/| | (_| | | | | | |_) | |_| | | | (_| |"
    echo " |____/ \\___\\___/ \\__,_|\\__| |_|   |_|\\__,_|_| |_| |____/ \\__,_|_|_|\\__,_|"
    echo -e "${NC}"
    echo -e "  ${DIM}AI-Assisted Development Workflow Framework${NC}"
    echo -e "  ${DIM}Version ${VERSION}${NC}"
    echo ""

    # Run installation steps
    run_preflight_checks "$target" "$force" || exit 1

    if [[ "$dry_run" != "true" ]]; then
        download_framework || exit 1
    else
        info "Skipping download (dry run)"
        mkdir -p "$TEMP_DIR/repo/.claude/commands"
        mkdir -p "$TEMP_DIR/repo/adws"
        mkdir -p "$TEMP_DIR/repo/.claude/hooks"
        mkdir -p "$TEMP_DIR/repo/.claude/skills"
        mkdir -p "$TEMP_DIR/repo/scripts"
    fi

    run_installation "$target" "$mode" "$dry_run" || exit 1

    if [[ "$dry_run" != "true" ]]; then
        show_next_steps "$target" "$mode"
    fi

    echo -e "${GREEN}${BOLD}Installation successful!${NC}"
    echo ""
}

# Run main
main "$@"
