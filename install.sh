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
MODE_INTERACTIVE="interactive"
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

# Spinner characters for progress display
readonly SPINNER=('|' '/' '-' '\')

# =============================================================================
# Interactive Mode Detection and TTY Handling
# =============================================================================

# Track interactive mode TTY source
INTERACTIVE_TTY=""

detect_interactive_mode() {
    local force_interactive="$1"

    # Check for explicit --interactive flag
    if [[ "$force_interactive" == "true" ]]; then
        # When forced, try to find a TTY for input
        if [[ -t 1 ]] && [[ -r /dev/tty ]]; then
            export INTERACTIVE_TTY="/dev/tty"
            return 0  # Interactive
        elif [[ -t 0 ]]; then
            export INTERACTIVE_TTY="/dev/stdin"
            return 0  # Interactive
        else
            warn "Cannot enable interactive mode - no TTY available"
            return 1  # Non-interactive
        fi
    fi

    # When piped via curl, stdin is not a TTY
    # We need to read from /dev/tty for user input
    if [[ ! -t 0 ]]; then
        # stdin is not a TTY (likely piped)
        # Check if we can access /dev/tty for interactive input
        if [[ -t 1 ]] && [[ -r /dev/tty ]]; then
            # stdout is TTY and we can read from /dev/tty
            # This allows interactive mode when piped via curl
            export INTERACTIVE_TTY="/dev/tty"
            return 0  # Interactive
        else
            return 1  # Non-interactive
        fi
    else
        # stdin is a TTY (normal terminal execution)
        export INTERACTIVE_TTY="/dev/stdin"
        return 0  # Interactive
    fi
}

# Read user input (works with curl piping)
read_user_input() {
    local prompt="$1"
    local default="$2"
    local response=""

    echo -n "$prompt" >&2

    if [[ -n "$INTERACTIVE_TTY" ]]; then
        read -r response < "$INTERACTIVE_TTY"
    else
        read -r response
    fi

    # Use default if response is empty
    echo "${response:-$default}"
}

# =============================================================================
# Component Selection State Management
# =============================================================================

# Associative array for component state (0=off, 1=on)
declare -A COMPONENT_STATE

# Initialize default selections based on preset
init_component_state() {
    local preset="${1:-standard}"

    # Slash command categories
    COMPONENT_STATE["planning"]=0
    COMPONENT_STATE["workflow"]=0
    COMPONENT_STATE["git"]=0
    COMPONENT_STATE["testing"]=0
    COMPONENT_STATE["session"]=0
    COMPONENT_STATE["analysis"]=0
    COMPONENT_STATE["utilities"]=0

    # Advanced components
    COMPONENT_STATE["python_adw"]=0
    COMPONENT_STATE["hooks"]=0
    COMPONENT_STATE["skills"]=0
    COMPONENT_STATE["scripts"]=0

    # Apply preset
    case "$preset" in
        minimal)
            COMPONENT_STATE["planning"]=1
            COMPONENT_STATE["workflow"]=1
            ;;
        standard)
            COMPONENT_STATE["planning"]=1
            COMPONENT_STATE["workflow"]=1
            COMPONENT_STATE["python_adw"]=1
            ;;
        full)
            for key in "${!COMPONENT_STATE[@]}"; do
                COMPONENT_STATE["$key"]=1
            done
            ;;
    esac
}

# Toggle component selection
toggle_component() {
    local component="$1"

    if [[ "${COMPONENT_STATE[$component]}" == "1" ]]; then
        COMPONENT_STATE["$component"]=0
    else
        COMPONENT_STATE["$component"]=1
    fi
}

# Toggle all components on or off
toggle_all() {
    local target_state="$1"  # "on" or "off"

    local new_state
    if [[ "$target_state" == "on" ]]; then
        new_state=1
    else
        new_state=0
    fi

    for key in "${!COMPONENT_STATE[@]}"; do
        COMPONENT_STATE["$key"]=$new_state
    done
}

# Get selection indicator for display
get_indicator() {
    local component="$1"

    if [[ "${COMPONENT_STATE[$component]}" == "1" ]]; then
        echo -e "${GREEN}+${NC}"
    else
        echo -e "${DIM}o${NC}"
    fi
}

# Count selected components
count_selected() {
    local count=0
    for key in "${!COMPONENT_STATE[@]}"; do
        if [[ "${COMPONENT_STATE[$key]}" == "1" ]]; then
            ((count++))
        fi
    done
    echo "$count"
}

# =============================================================================
# Interactive Menu Display
# =============================================================================

show_component_menu() {
    clear

    cat << EOF
${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}
${BOLD}  Scout-Plan-Build Framework Installer v${VERSION}${NC}
${BOLD}  Interactive Component Selection${NC}
${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}

${BOLD}CORE${NC} (Always Installed)
  + Directory structure
  + Configuration files (.adw_config.json, .env.template)
  + Documentation (CLAUDE.md)

${BOLD}SLASH COMMANDS${NC} (Select categories)
  ${DIM}[1]${NC} $(get_indicator planning) Planning Commands        ${DIM}(plan, scout, design)${NC}
  ${DIM}[2]${NC} $(get_indicator workflow) Workflow Commands        ${DIM}(implement, build)${NC}
  ${DIM}[3]${NC} $(get_indicator git) Git Commands             ${DIM}(worktree, branch, PR)${NC}
  ${DIM}[4]${NC} $(get_indicator testing) Testing Commands         ${DIM}(test, e2e, validate)${NC}
  ${DIM}[5]${NC} $(get_indicator session) Session Commands         ${DIM}(save, resume, compact)${NC}
  ${DIM}[6]${NC} $(get_indicator analysis) Analysis Commands        ${DIM}(analyze, review, doc)${NC}
  ${DIM}[7]${NC} $(get_indicator utilities) Utility Commands         ${DIM}(install, prepare)${NC}

${BOLD}ADVANCED COMPONENTS${NC}
  ${DIM}[8]${NC}  $(get_indicator python_adw) Python ADW System        ${DIM}(adws/ orchestration)${NC}
  ${DIM}[9]${NC}  $(get_indicator hooks) Event Hooks              ${DIM}(.claude/hooks/)${NC}
  ${DIM}[10]${NC} $(get_indicator skills) Skills                   ${DIM}(advanced workflows)${NC}
  ${DIM}[11]${NC} $(get_indicator scripts) Scripts                  ${DIM}(bash utilities)${NC}

${BOLD}QUICK PRESETS${NC}
  ${DIM}[M]${NC} Minimal   - Commands only (1-2)
  ${DIM}[S]${NC} Standard  - Commands + ADW (1-2, 8)
  ${DIM}[F]${NC} Full      - Everything (1-11)
  ${DIM}[A]${NC} Toggle All / None

${DIM}[ENTER]${NC} Continue with selection
${DIM}[Q]${NC}     Quit

${CYAN}Current selection: $(count_selected) components${NC}

EOF

    echo -n "Select option: "
}

# Handle menu selection input
handle_menu_selection() {
    local choice
    choice=$(read_user_input "" "")

    case "$choice" in
        1) toggle_component "planning" ;;
        2) toggle_component "workflow" ;;
        3) toggle_component "git" ;;
        4) toggle_component "testing" ;;
        5) toggle_component "session" ;;
        6) toggle_component "analysis" ;;
        7) toggle_component "utilities" ;;
        8) toggle_component "python_adw" ;;
        9) toggle_component "hooks" ;;
        10) toggle_component "skills" ;;
        11) toggle_component "scripts" ;;

        [Mm])
            init_component_state "minimal"
            ;;
        [Ss])
            init_component_state "standard"
            ;;
        [Ff])
            init_component_state "full"
            ;;
        [Aa])
            local current_count
            current_count=$(count_selected)
            if [[ "$current_count" -gt 0 ]]; then
                toggle_all "off"
            else
                toggle_all "on"
            fi
            ;;
        "")
            # Enter pressed - continue with installation
            return 0
            ;;
        [Qq])
            error "Installation cancelled by user"
            exit 0
            ;;
        *)
            warn "Invalid selection: $choice"
            sleep 1
            ;;
    esac

    # Continue showing menu (return 1 to loop)
    return 1
}

# Run interactive menu loop
run_interactive_menu() {
    init_component_state "standard"  # Start with standard preset

    while true; do
        show_component_menu
        if handle_menu_selection; then
            break  # User pressed Enter to continue
        fi
    done
}

# =============================================================================
# Installation Summary and Confirmation
# =============================================================================

show_installation_summary() {
    local target="$1"

    # Calculate component counts
    local cmd_categories=0
    local cmd_count=0
    local adv_components=0

    # Count selected command categories
    for cat in planning workflow git testing session analysis utilities; do
        if [[ "${COMPONENT_STATE[$cat]}" == "1" ]]; then
            ((cmd_categories++))
            # Estimate files per category (approximation)
            case "$cat" in
                planning) ((cmd_count += 6)) ;;
                workflow) ((cmd_count += 9)) ;;
                git) ((cmd_count += 11)) ;;
                testing) ((cmd_count += 4)) ;;
                session) ((cmd_count += 4)) ;;
                analysis) ((cmd_count += 4)) ;;
                utilities) ((cmd_count += 6)) ;;
            esac
        fi
    done

    # Count advanced components
    for comp in python_adw hooks skills scripts; do
        if [[ "${COMPONENT_STATE[$comp]}" == "1" ]]; then
            ((adv_components++))
        fi
    done

    # Estimate disk space
    local disk_space="500 KB"  # Base
    [[ "${COMPONENT_STATE[python_adw]}" == "1" ]] && disk_space="2.5 MB"

    cat << EOF

${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}
${BOLD}  Installation Summary${NC}
${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}

${BOLD}Target:${NC} $target
${BOLD}Mode:${NC}   Interactive (Custom selection)

${BOLD}Will install:${NC}
  + Core directory structure
EOF

    # Show selected command categories
    if [[ "$cmd_categories" -gt 0 ]]; then
        echo "  + Slash commands: $cmd_categories categories ($cmd_count commands)"
        [[ "${COMPONENT_STATE[planning]}" == "1" ]] && echo "    - Planning Commands"
        [[ "${COMPONENT_STATE[workflow]}" == "1" ]] && echo "    - Workflow Commands"
        [[ "${COMPONENT_STATE[git]}" == "1" ]] && echo "    - Git Commands"
        [[ "${COMPONENT_STATE[testing]}" == "1" ]] && echo "    - Testing Commands"
        [[ "${COMPONENT_STATE[session]}" == "1" ]] && echo "    - Session Commands"
        [[ "${COMPONENT_STATE[analysis]}" == "1" ]] && echo "    - Analysis Commands"
        [[ "${COMPONENT_STATE[utilities]}" == "1" ]] && echo "    - Utility Commands"
    fi

    # Show selected advanced components
    [[ "${COMPONENT_STATE[python_adw]}" == "1" ]] && echo "  + Python ADW System (12 modules)"
    [[ "${COMPONENT_STATE[hooks]}" == "1" ]] && echo "  + Event Hooks (8 hooks)"
    [[ "${COMPONENT_STATE[skills]}" == "1" ]] && echo "  + Skills (2 workflow skills)"
    [[ "${COMPONENT_STATE[scripts]}" == "1" ]] && echo "  + Utility Scripts (4 scripts)"

    cat << EOF

${BOLD}Disk space required:${NC} ~$disk_space
${BOLD}Estimated time:${NC} 30-60 seconds

EOF
}

confirm_installation() {
    local response
    response=$(read_user_input "Proceed with installation? [Y/n] " "Y")

    if [[ "$response" =~ ^[Yy]$ ]] || [[ -z "$response" ]]; then
        return 0  # Proceed
    else
        error "Installation cancelled by user"
        exit 0
    fi
}

# =============================================================================
# Component-Based Installation Functions
# =============================================================================

install_slash_command_category() {
    local source="$1"
    local target="$2"
    local category="$3"
    local dry_run="$4"

    # Only install if selected
    if [[ "${COMPONENT_STATE[$category]}" != "1" ]]; then
        return 0
    fi

    local cmd_dir="$source/.claude/commands/$category"

    if [[ ! -d "$cmd_dir" ]]; then
        warn "Command category directory not found: $category"
        return 0
    fi

    info "Installing $category commands..."

    local count=0
    while IFS= read -r -d '' file; do
        if [[ "$dry_run" == "true" ]]; then
            step_pending "Would copy: .claude/commands/$category/$(basename "$file")"
        else
            mkdir -p "$target/.claude/commands/$category"
            cp "$file" "$target/.claude/commands/$category/"
            ((count++))
        fi
    done < <(find "$cmd_dir" -maxdepth 1 -type f -name "*.md" -print0)

    if [[ "$dry_run" != "true" ]]; then
        step "Installed $count $category commands"
    fi
}

install_advanced_component() {
    local source="$1"
    local target="$2"
    local component="$3"
    local dry_run="$4"

    # Only install if selected
    if [[ "${COMPONENT_STATE[$component]}" != "1" ]]; then
        return 0
    fi

    case "$component" in
        python_adw)
            if [[ -d "$source/adws" ]]; then
                if [[ "$dry_run" == "true" ]]; then
                    step_pending "Would copy: adws/ (Python modules)"
                else
                    cp -r "$source/adws" "$target/"
                    step "Installed Python ADW System"
                fi
            fi
            ;;
        hooks)
            if [[ -d "$source/.claude/hooks" ]]; then
                if [[ "$dry_run" == "true" ]]; then
                    step_pending "Would copy: .claude/hooks/"
                else
                    cp -r "$source/.claude/hooks" "$target/.claude/"
                    step "Installed Event Hooks"
                fi
            fi
            ;;
        skills)
            if [[ -d "$source/.claude/skills" ]]; then
                if [[ "$dry_run" == "true" ]]; then
                    step_pending "Would copy: .claude/skills/"
                else
                    cp -r "$source/.claude/skills" "$target/.claude/"
                    step "Installed Skills"
                fi
            fi
            ;;
        scripts)
            if [[ -d "$source/scripts" ]]; then
                if [[ "$dry_run" == "true" ]]; then
                    step_pending "Would copy: scripts/"
                else
                    mkdir -p "$target/scripts"
                    cp "$source/scripts/"*.sh "$target/scripts/" 2>/dev/null || true
                    chmod +x "$target/scripts/"*.sh 2>/dev/null || true
                    step "Installed Utility Scripts"
                fi
            fi
            ;;
    esac
}

# Main installation with component selection
run_component_installation() {
    local source="$1"
    local target="$2"
    local dry_run="$3"

    header "Installing Components"
    echo ""

    # Always install core
    info "Installing core components..."
    create_directories "$target" "$dry_run"
    generate_env_template "$target" "$dry_run"
    generate_config "$target" "$dry_run"
    generate_claude_md "$target" "$MODE_INTERACTIVE" "$dry_run"
    generate_install_info "$target" "$MODE_INTERACTIVE" "$dry_run"
    echo ""

    # Install selected slash command categories
    info "Installing slash commands..."
    for category in planning workflow git testing session analysis utilities; do
        install_slash_command_category "$source" "$target" "$category" "$dry_run"
    done
    echo ""

    # Install selected advanced components
    info "Installing advanced components..."
    for component in python_adw hooks skills scripts; do
        install_advanced_component "$source" "$target" "$component" "$dry_run"
    done
    echo ""

    if [[ "$dry_run" == "true" ]]; then
        success "Dry run complete - no changes made"
    else
        success "Installation complete"
    fi
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
    # Quick install (minimal)
    curl -sL ${REPO_URL}/raw/main/install.sh | bash -s /path/to/target

    # Interactive selection
    ./install.sh /path/to/target --interactive

    # Force interactive with curl piping
    curl -sL URL | bash -s -- /path/to/target --interactive

${BOLD}ARGUMENTS:${NC}
    TARGET              Target directory for installation (required)
                        Must be an existing, writable directory

${BOLD}OPTIONS:${NC}
    --minimal           Install slash commands only (default for piped)
    --full              Install everything (all components)
    --interactive       Show interactive menu for component selection
    --dry-run           Show what would be installed without making changes
    --force             Overwrite existing installation without prompting
    --help, -h          Show this help message

${BOLD}INSTALLATION MODES:${NC}
    ${GREEN}Minimal${NC}         - Essential commands only (planning + workflow)
    ${GREEN}Standard${NC}        - Recommended setup (commands + Python ADW)
    ${GREEN}Full${NC}            - Complete installation (all components)
    ${GREEN}Interactive${NC}     - Custom component selection via menu

${BOLD}EXAMPLES:${NC}
    # Quick minimal install
    curl -sL ${REPO_URL}/raw/main/install.sh | bash -s ./my-project

    # Full installation
    curl -sL ${REPO_URL}/raw/main/install.sh | bash -s -- ./my-project --full

    # Interactive selection (local execution)
    ./install.sh ./my-project --interactive

    # Interactive via curl (requires TTY)
    curl -sL URL | bash -s -- ./my-project --interactive

    # Preview what would be installed
    ./install.sh ./my-project --interactive --dry-run

${BOLD}COMPONENT CATEGORIES (Interactive Mode):${NC}
    Slash Commands:
      [1] Planning   - plan, scout, design commands
      [2] Workflow   - implement, build commands
      [3] Git        - worktree, branch, PR commands
      [4] Testing    - test, e2e, validate commands
      [5] Session    - save, resume, compact commands
      [6] Analysis   - analyze, review, doc commands
      [7] Utilities  - install, prepare commands

    Advanced Components:
      [8]  Python ADW - adws/ orchestration modules
      [9]  Hooks      - .claude/hooks/ event automation
      [10] Skills     - advanced workflow patterns
      [11] Scripts    - bash utility scripts

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

    # Show validation step for full install or if scripts were selected in interactive mode
    if [[ "$mode" == "$MODE_FULL" ]]; then
        echo "  4. Validate installation:"
        echo "     ${CYAN}./scripts/validate_pipeline.sh${NC}"
        echo ""
    elif [[ "$mode" == "$MODE_INTERACTIVE" ]] && [[ "${COMPONENT_STATE[scripts]}" == "1" ]]; then
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
    local mode=""  # Will be set based on interactive/non-interactive
    local dry_run="false"
    local force="false"
    local use_interactive="false"

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --help|-h)
                show_help
                ;;
            --minimal)
                mode="$MODE_MINIMAL"
                use_interactive="false"
                shift
                ;;
            --full)
                mode="$MODE_FULL"
                use_interactive="false"
                shift
                ;;
            --interactive)
                use_interactive="true"
                mode=""  # Will be set via menu
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

    # Detect interactive mode if not explicitly set via flags
    if [[ -z "$mode" ]] && [[ "$use_interactive" != "true" ]]; then
        # No mode specified - check if we should auto-enable interactive
        if detect_interactive_mode "false"; then
            # TTY available but user didn't specify mode
            # Default to minimal for backward compatibility
            mode="$MODE_MINIMAL"
        else
            # Non-interactive, use minimal as default
            mode="$MODE_MINIMAL"
        fi
    fi

    # If --interactive was requested, verify TTY availability
    if [[ "$use_interactive" == "true" ]]; then
        if ! detect_interactive_mode "true"; then
            error "Interactive mode requires a terminal (TTY)"
            echo "Falling back to --minimal mode"
            mode="$MODE_MINIMAL"
            use_interactive="false"
        fi
    fi

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

    # Run pre-flight checks
    run_preflight_checks "$target" "$force" || exit 1

    # Download framework (needed for all modes)
    if [[ "$dry_run" != "true" ]]; then
        download_framework || exit 1
    else
        info "Skipping download (dry run)"
        mkdir -p "$TEMP_DIR/repo/.claude/commands/planning"
        mkdir -p "$TEMP_DIR/repo/.claude/commands/workflow"
        mkdir -p "$TEMP_DIR/repo/.claude/commands/git"
        mkdir -p "$TEMP_DIR/repo/.claude/commands/testing"
        mkdir -p "$TEMP_DIR/repo/.claude/commands/session"
        mkdir -p "$TEMP_DIR/repo/.claude/commands/analysis"
        mkdir -p "$TEMP_DIR/repo/.claude/commands/utilities"
        mkdir -p "$TEMP_DIR/repo/adws"
        mkdir -p "$TEMP_DIR/repo/.claude/hooks"
        mkdir -p "$TEMP_DIR/repo/.claude/skills"
        mkdir -p "$TEMP_DIR/repo/scripts"
    fi

    local source="$TEMP_DIR/repo"

    # Run installation based on mode
    if [[ "$use_interactive" == "true" ]]; then
        # Interactive menu mode
        run_interactive_menu
        show_installation_summary "$target"
        confirm_installation
        run_component_installation "$source" "$target" "$dry_run"
        mode="$MODE_INTERACTIVE"  # For next steps display
    else
        # Non-interactive (--minimal or --full)
        run_installation "$target" "$mode" "$dry_run" || exit 1
    fi

    # Show next steps
    if [[ "$dry_run" != "true" ]]; then
        show_next_steps "$target" "$mode"
    fi

    echo -e "${GREEN}${BOLD}Installation successful!${NC}"
    echo ""
}

# Run main
main "$@"
