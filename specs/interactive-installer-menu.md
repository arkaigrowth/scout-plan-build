# Interactive Installer Menu System - Design Specification

**Version**: 1.0
**Date**: 2025-11-26
**Author**: System Architecture Team
**Status**: Design Phase

## Executive Summary

Design a numbered menu system for the Scout-Plan-Build framework installer that provides interactive component selection while maintaining compatibility with non-interactive modes (curl piping). The system must be pure bash with no external dependencies.

---

## 1. Menu Flow Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  Scout-Plan-Build Framework Installer v1.0.0                 │
│  Interactive Component Selection                             │
└──────────────────────────────────────────────────────────────┘

┌─ STEP 1: Mode Detection ─────────────────────────────────────┐
│                                                               │
│  Is stdin a TTY?                                              │
│  ├─ NO  → Non-interactive (curl piped)                       │
│  │        Use --minimal, --full, or --interactive flag       │
│  │                                                            │
│  └─ YES → Interactive TTY detected                           │
│           Show menu system                                   │
│                                                               │
└───────────────────────────────────────────────────────────────┘
                              ↓
┌─ STEP 2: Component Selection Menu ──────────────────────────┐
│                                                               │
│  INSTALLATION COMPONENTS                                      │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━                                   │
│                                                               │
│  CORE (Always Installed)                                      │
│    ✓ Directory structure                                      │
│    ✓ Configuration files (.adw_config.json, .env.template)   │
│    ✓ Documentation (CLAUDE.md)                               │
│                                                               │
│  SLASH COMMANDS (Select categories)                          │
│    [1] ✓ Planning Commands        (plan, scout, design)      │
│    [2] ✓ Workflow Commands         (implement, build)        │
│    [3] ○ Git Commands              (worktree, branch, PR)    │
│    [4] ○ Testing Commands          (test, e2e, validate)     │
│    [5] ○ Session Commands          (save, resume, compact)   │
│    [6] ○ Analysis Commands         (analyze, review, doc)    │
│    [7] ○ Utility Commands          (install, prepare)        │
│                                                               │
│  ADVANCED COMPONENTS                                          │
│    [8] ○ Python ADW System         (adws/ modules)           │
│    [9] ○ Event Hooks               (.claude/hooks/)          │
│   [10] ○ Skills                    (advanced workflows)       │
│   [11] ○ Scripts                   (bash utilities)          │
│                                                               │
│  QUICK PRESETS                                                │
│    [M] Minimal    - Commands only (1-2)                      │
│    [S] Standard   - Commands + ADW (1-8)                     │
│    [F] Full       - Everything (1-11)                        │
│    [A] Toggle All / None                                      │
│                                                               │
│  [ENTER] Continue with selection                             │
│  [Q] Quit                                                     │
│                                                               │
│  Current selection: Standard (8 components)                   │
│                                                               │
└───────────────────────────────────────────────────────────────┘
                              ↓
┌─ STEP 3: Confirmation ───────────────────────────────────────┐
│                                                               │
│  INSTALLATION SUMMARY                                         │
│  ━━━━━━━━━━━━━━━━━━━━━                                       │
│                                                               │
│  Target: /Users/alex/projects/my-app                         │
│  Mode:   Interactive (Standard preset)                       │
│                                                               │
│  Will install:                                                │
│    ✓ Core directory structure                                │
│    ✓ Planning commands (3 commands)                          │
│    ✓ Workflow commands (5 commands)                          │
│    ✓ Python ADW System (12 modules)                          │
│                                                               │
│  Disk space required: ~2.5 MB                                 │
│  Estimated time: 30 seconds                                   │
│                                                               │
│  Proceed with installation? [Y/n]                            │
│                                                               │
└───────────────────────────────────────────────────────────────┘
                              ↓
┌─ STEP 4: Installation Progress ──────────────────────────────┐
│                                                               │
│  [1/4] Creating directories...            ✓                  │
│  [2/4] Installing slash commands...       ⣾  (12/18)         │
│  [3/4] Installing Python modules...       ○                  │
│  [4/4] Generating configuration...        ○                  │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

---

## 2. Component Categories & Mapping

### 2.1 Core (Always Installed)
```yaml
category: core
auto_install: true
selectable: false
components:
  - Directory structure (specs/, scout_outputs/, ai_docs/)
  - Configuration files (.adw_config.json)
  - Environment template (.env.template)
  - Project documentation (CLAUDE.md)
  - Install metadata (.scout_install_info.json)
```

### 2.2 Slash Commands (Categorized by Directory)

```yaml
category: slash_commands
subdivisions:

  planning:
    label: "Planning Commands"
    description: "Scout, plan, design workflows"
    menu_number: 1
    default: true
    files:
      - .claude/commands/planning/plan_w_docs.md
      - .claude/commands/planning/plan_w_docs_improved.md
      - .claude/commands/planning/feature.md
      - .claude/commands/planning/bug.md
      - .claude/commands/planning/chore.md
      - .claude/commands/planning/patch.md

  workflow:
    label: "Workflow Commands"
    description: "Build, implement, execute"
    menu_number: 2
    default: true
    files:
      - .claude/commands/workflow/build_adw.md
      - .claude/commands/workflow/build.md
      - .claude/commands/workflow/implement.md
      - .claude/commands/workflow/scout.md
      - .claude/commands/workflow/scout_improved.md
      - .claude/commands/workflow/scout_fixed.md
      - .claude/commands/workflow/scout_parallel.md
      - .claude/commands/workflow/scout_plan_build.md
      - .claude/commands/workflow/scout_plan_build_improved.md

  git:
    label: "Git Commands"
    description: "Worktree, branch, commit, PR"
    menu_number: 3
    default: false
    files:
      - .claude/commands/git/worktree_create.md
      - .claude/commands/git/worktree_checkpoint.md
      - .claude/commands/git/worktree_undo.md
      - .claude/commands/git/worktree_redo.md
      - .claude/commands/git/init-parallel-worktrees.md
      - .claude/commands/git/compare-worktrees.md
      - .claude/commands/git/merge-worktree.md
      - .claude/commands/git/run-parallel-agents.md
      - .claude/commands/git/generate_branch_name.md
      - .claude/commands/git/commit.md
      - .claude/commands/git/pull_request.md

  testing:
    label: "Testing Commands"
    description: "Test, validate, review"
    menu_number: 4
    default: false
    files:
      - .claude/commands/testing/test.md
      - .claude/commands/testing/test_e2e.md
      - .claude/commands/testing/resolve_failed_test.md
      - .claude/commands/testing/resolve_failed_e2e_test.md

  session:
    label: "Session Commands"
    description: "Save, resume, compact state"
    menu_number: 5
    default: false
    files:
      - .claude/commands/session/prime.md
      - .claude/commands/session/start.md
      - .claude/commands/session/resume.md
      - .claude/commands/session/prepare-compaction.md

  analysis:
    label: "Analysis Commands"
    description: "Analyze, review, document"
    menu_number: 6
    default: false
    files:
      - .claude/commands/analysis/document.md
      - .claude/commands/analysis/review.md
      - .claude/commands/analysis/classify_adw.md
      - .claude/commands/analysis/classify_issue.md

  utilities:
    label: "Utility Commands"
    description: "Install, prepare, tools"
    menu_number: 7
    default: false
    files:
      - .claude/commands/utilities/init-framework.md
      - .claude/commands/utilities/install.md
      - .claude/commands/utilities/prepare_app.md
      - .claude/commands/utilities/conditional_docs.md
      - .claude/commands/utilities/research-add.md
      - .claude/commands/utilities/tools.md
```

### 2.3 Advanced Components

```yaml
category: advanced

python_adw:
  label: "Python ADW System"
  description: "Core workflow orchestration (adws/)"
  menu_number: 8
  default: false
  size: "~2 MB"
  source: "adws/"
  destination: "adws/"
  files: all

hooks:
  label: "Event Hooks"
  description: "Observability and automation (.claude/hooks/)"
  menu_number: 9
  default: false
  size: "~50 KB"
  source: ".claude/hooks/"
  destination: ".claude/hooks/"
  files: all

skills:
  label: "Skills"
  description: "Advanced workflow patterns (.claude/skills/)"
  menu_number: 10
  default: false
  size: "~100 KB"
  source: ".claude/skills/"
  destination: ".claude/skills/"
  files: all

scripts:
  label: "Scripts"
  description: "Bash utility scripts (scripts/)"
  menu_number: 11
  default: false
  size: "~75 KB"
  source: "scripts/"
  destination: "scripts/"
  files:
    - validate_pipeline.sh
    - workflow.sh
    - worktree_manager.sh
    - fix_agents_naming.sh
```

---

## 3. Bash Implementation

### 3.1 TTY Detection & Mode Selection

```bash
#!/usr/bin/env bash

# =============================================================================
# Interactive Mode Detection
# =============================================================================

detect_interactive_mode() {
    local force_interactive="$1"

    # Check for explicit --interactive flag
    if [[ "$force_interactive" == "true" ]]; then
        return 0  # Interactive
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
```

### 3.2 Component State Management

```bash
# =============================================================================
# Component Selection State
# =============================================================================

# Associative array for component state (0=off, 1=on)
declare -A COMPONENT_STATE

# Initialize default selections
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

# Toggle all components
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

# Get selection indicator
get_indicator() {
    local component="$1"

    if [[ "${COMPONENT_STATE[$component]}" == "1" ]]; then
        echo "✓"
    else
        echo "○"
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
```

### 3.3 Menu Display Functions

```bash
# =============================================================================
# Menu Display
# =============================================================================

show_component_menu() {
    clear

    cat << EOF
${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}
${BOLD}  Scout-Plan-Build Framework Installer v${VERSION}${NC}
${BOLD}  Interactive Component Selection${NC}
${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}

${BOLD}CORE${NC} (Always Installed)
  ✓ Directory structure
  ✓ Configuration files (.adw_config.json, .env.template)
  ✓ Documentation (CLAUDE.md)

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

# Handle menu selection
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
            # Enter pressed - continue
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
```

### 3.4 Installation Summary & Confirmation

```bash
# =============================================================================
# Installation Summary
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
    [[ "${COMPONENT_STATE[hooks]}" == "1" ]] && disk_space="$disk_space + 50 KB"

    cat << EOF

${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}
${BOLD}  Installation Summary${NC}
${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}

${BOLD}Target:${NC} $target
${BOLD}Mode:${NC}   Interactive (Custom selection)

${BOLD}Will install:${NC}
  ✓ Core directory structure
EOF

    # Show selected command categories
    if [[ "$cmd_categories" -gt 0 ]]; then
        echo "  ✓ Slash commands: $cmd_categories categories ($cmd_count commands)"
        [[ "${COMPONENT_STATE[planning]}" == "1" ]] && echo "    - Planning Commands"
        [[ "${COMPONENT_STATE[workflow]}" == "1" ]] && echo "    - Workflow Commands"
        [[ "${COMPONENT_STATE[git]}" == "1" ]] && echo "    - Git Commands"
        [[ "${COMPONENT_STATE[testing]}" == "1" ]] && echo "    - Testing Commands"
        [[ "${COMPONENT_STATE[session]}" == "1" ]] && echo "    - Session Commands"
        [[ "${COMPONENT_STATE[analysis]}" == "1" ]] && echo "    - Analysis Commands"
        [[ "${COMPONENT_STATE[utilities]}" == "1" ]] && echo "    - Utility Commands"
    fi

    # Show selected advanced components
    [[ "${COMPONENT_STATE[python_adw]}" == "1" ]] && echo "  ✓ Python ADW System (12 modules)"
    [[ "${COMPONENT_STATE[hooks]}" == "1" ]] && echo "  ✓ Event Hooks (8 hooks)"
    [[ "${COMPONENT_STATE[skills]}" == "1" ]] && echo "  ✓ Skills (2 workflow skills)"
    [[ "${COMPONENT_STATE[scripts]}" == "1" ]] && echo "  ✓ Utility Scripts (4 scripts)"

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
```

### 3.5 Component-Based Installation

```bash
# =============================================================================
# Component Installation
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
    generate_claude_md "$target" "interactive" "$dry_run"
    generate_install_info "$target" "interactive" "$dry_run"
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
```

### 3.6 Main Entry Point Integration

```bash
# =============================================================================
# Updated Main Entry Point
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
        exit 1
    fi

    # Convert to absolute path
    target=$(cd "$target" 2>/dev/null && pwd)

    # Detect interactive mode if not explicitly set
    if [[ -z "$mode" ]] && [[ "$use_interactive" != "true" ]]; then
        if detect_interactive_mode "$use_interactive"; then
            use_interactive="true"
        else
            # Non-interactive, use minimal as default
            mode="$MODE_MINIMAL"
        fi
    fi

    # Show banner
    show_banner

    # Run pre-flight checks
    run_preflight_checks "$target" "$force" || exit 1

    # Download framework
    if [[ "$dry_run" != "true" ]]; then
        download_framework || exit 1
    fi

    local source="$TEMP_DIR/repo"

    # Run installation based on mode
    if [[ "$use_interactive" == "true" ]]; then
        # Interactive menu
        run_interactive_menu
        show_installation_summary "$target"
        confirm_installation
        run_component_installation "$source" "$target" "$dry_run"
    else
        # Non-interactive (--minimal or --full)
        run_installation "$target" "$mode" "$dry_run"
    fi

    # Show next steps
    if [[ "$dry_run" != "true" ]]; then
        show_next_steps "$target" "$mode"
    fi

    echo -e "${GREEN}${BOLD}Installation successful!${NC}"
}
```

---

## 4. Non-Interactive Mode Compatibility

### 4.1 Command Line Flags

```bash
# All existing flags continue to work:

# Minimal (default for curl piping)
curl -sL URL | bash -s /path/to/target

# Explicit minimal
curl -sL URL | bash -s -- /path/to/target --minimal

# Full installation
curl -sL URL | bash -s -- /path/to/target --full

# Force interactive (requires TTY)
./install.sh /path/to/target --interactive

# Dry run
./install.sh /path/to/target --interactive --dry-run
```

### 4.2 Stdin Handling Strategy

```
┌─ Scenario 1: Local execution ───────────────────────────────┐
│  ./install.sh /path/to/target --interactive                  │
│  ├─ stdin: TTY                                                │
│  ├─ stdout: TTY                                               │
│  └─ Read from: /dev/stdin (normal)                           │
└───────────────────────────────────────────────────────────────┘

┌─ Scenario 2: Curl piping (non-interactive) ─────────────────┐
│  curl -sL URL | bash -s /path/to/target                      │
│  ├─ stdin: Pipe from curl (NOT TTY)                          │
│  ├─ stdout: TTY                                               │
│  └─ Mode: --minimal (automatic fallback)                     │
└───────────────────────────────────────────────────────────────┘

┌─ Scenario 3: Curl piping (force interactive) ───────────────┐
│  curl -sL URL | bash -s -- /path/to/target --interactive     │
│  ├─ stdin: Pipe from curl (NOT TTY)                          │
│  ├─ stdout: TTY                                               │
│  ├─ Read from: /dev/tty (direct terminal access)             │
│  └─ Mode: Interactive menu                                    │
└───────────────────────────────────────────────────────────────┘

┌─ Scenario 4: Fully automated (CI/CD) ───────────────────────┐
│  curl -sL URL | bash -s -- /path/to/target --full --force    │
│  ├─ stdin: Pipe                                               │
│  ├─ stdout: Pipe or file                                      │
│  └─ Mode: --full (no prompts)                                │
└───────────────────────────────────────────────────────────────┘
```

---

## 5. User Experience Features

### 5.1 Visual Indicators

```bash
# Component states
✓  Selected (green)
○  Not selected (dim)

# Progress indicators
[1/4] Creating directories...     ✓   Completed
[2/4] Installing commands...      ⣾   In progress with spinner
[3/4] Installing modules...       ○   Pending

# Spinners (simple ASCII-based, no Unicode dependencies)
SPINNER_CHARS=('⠋' '⠙' '⠹' '⠸' '⠼' '⠴' '⠦' '⠧' '⠇' '⠏')
# Fallback for non-Unicode: ('|' '/' '-' '\')
```

### 5.2 Smart Defaults

```yaml
# Default preset: Standard
default:
  - planning: true      # Essential for workflow
  - workflow: true      # Essential for workflow
  - git: false          # Advanced users only
  - testing: false      # Add when needed
  - session: false      # Add when needed
  - analysis: false     # Add when needed
  - utilities: false    # Add when needed
  - python_adw: true    # Recommended for full workflow
  - hooks: false        # Advanced
  - skills: false       # Advanced
  - scripts: false      # Optional utilities

# Preset mappings
minimal:   [planning, workflow]
standard:  [planning, workflow, python_adw]
full:      [all components]
```

### 5.3 Installation Progress

```bash
show_progress() {
    local current="$1"
    local total="$2"
    local task="$3"
    local status="$4"  # "active", "done", "pending"

    local indicator
    case "$status" in
        done)    indicator="${GREEN}✓${NC}" ;;
        active)  indicator="${YELLOW}⣾${NC}" ;;
        pending) indicator="${DIM}○${NC}" ;;
    esac

    printf "  [%d/%d] %-40s %s\n" "$current" "$total" "$task" "$indicator"
}

# Usage
show_progress 1 4 "Creating directories..." "done"
show_progress 2 4 "Installing slash commands..." "active"
show_progress 3 4 "Installing Python modules..." "pending"
show_progress 4 4 "Generating configuration..." "pending"
```

---

## 6. Testing Strategy

### 6.1 Test Scenarios

```bash
# Test 1: Local interactive execution
./install.sh /tmp/test-install --interactive

# Test 2: Local minimal (non-interactive)
./install.sh /tmp/test-install --minimal

# Test 3: Local full (non-interactive)
./install.sh /tmp/test-install --full

# Test 4: Curl piped (non-interactive default)
curl -sL localhost:8000/install.sh | bash -s /tmp/test-install

# Test 5: Curl piped with interactive flag
curl -sL localhost:8000/install.sh | bash -s -- /tmp/test-install --interactive

# Test 6: Dry run interactive
./install.sh /tmp/test-install --interactive --dry-run

# Test 7: Force mode (no prompts)
./install.sh /tmp/test-install --full --force
```

### 6.2 Validation Checks

```bash
# After installation, validate:
test -d /tmp/test-install/specs || echo "FAIL: specs directory missing"
test -d /tmp/test-install/.claude/commands || echo "FAIL: commands missing"
test -f /tmp/test-install/.adw_config.json || echo "FAIL: config missing"

# If Python ADW selected:
test -d /tmp/test-install/adws || echo "FAIL: adws missing"

# If hooks selected:
test -d /tmp/test-install/.claude/hooks || echo "FAIL: hooks missing"
```

---

## 7. Documentation Updates

### 7.1 Updated Help Text

```bash
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

${BOLD}OPTIONS:${NC}
    --minimal           Install slash commands only (default for piped)
    --full              Install everything (all components)
    --interactive       Show interactive menu for component selection
    --dry-run           Preview installation without making changes
    --force             Skip confirmation prompts
    --help, -h          Show this help

${BOLD}INSTALLATION MODES:${NC}
    ${GREEN}Minimal${NC}         - Essential commands only (planning + workflow)
    ${GREEN}Standard${NC}        - Recommended setup (commands + Python ADW)
    ${GREEN}Full${NC}            - Complete installation (all components)
    ${GREEN}Interactive${NC}     - Custom component selection via menu

${BOLD}EXAMPLES:${NC}
    # Quick minimal install
    curl -sL URL | bash -s ./my-project

    # Full installation
    curl -sL URL | bash -s -- ./my-project --full

    # Interactive selection (local)
    ./install.sh ./my-project --interactive

    # Interactive via curl (requires TTY)
    curl -sL URL | bash -s -- ./my-project --interactive

EOF
}
```

### 7.2 README Updates

```markdown
## Installation

### Quick Start (Minimal)
```bash
curl -sL https://raw.githubusercontent.com/arkaigrowth/scout-plan-build/main/install.sh | bash -s /path/to/your/project
```

### Interactive Selection
```bash
# Download and run locally for interactive menu
curl -sL URL -o install.sh
chmod +x install.sh
./install.sh /path/to/your/project --interactive
```

### Full Installation
```bash
curl -sL URL | bash -s -- /path/to/your/project --full
```

## Installation Modes

| Mode | Components | Use Case |
|------|------------|----------|
| **Minimal** | Planning + Workflow commands | Quick evaluation, small projects |
| **Standard** | Minimal + Python ADW System | Recommended for full workflow |
| **Full** | All components | Complete tooling, CI/CD integration |
| **Interactive** | Custom selection | Tailored installation |
```

---

## 8. Implementation Checklist

### Phase 1: Core Menu System
- [ ] Implement `detect_interactive_mode()` with /dev/tty handling
- [ ] Implement `read_user_input()` for curl-piped stdin
- [ ] Create component state management (associative arrays)
- [ ] Build `show_component_menu()` display function
- [ ] Implement `handle_menu_selection()` input handler

### Phase 2: Installation Logic
- [ ] Create `install_slash_command_category()` function
- [ ] Create `install_advanced_component()` function
- [ ] Implement `run_component_installation()` orchestrator
- [ ] Add installation summary display
- [ ] Add confirmation prompt

### Phase 3: Integration
- [ ] Update `main()` entry point with mode detection
- [ ] Add `--interactive` flag parsing
- [ ] Integrate with existing `--minimal` and `--full` modes
- [ ] Update help text and documentation

### Phase 4: Testing
- [ ] Test local interactive execution
- [ ] Test curl piping with default (minimal)
- [ ] Test curl piping with `--interactive` flag
- [ ] Test dry-run mode
- [ ] Test all component combinations
- [ ] Test on Linux and macOS

### Phase 5: Documentation
- [ ] Update README with new installation modes
- [ ] Update inline help text
- [ ] Add examples for all scenarios
- [ ] Document stdin handling strategy

---

## 9. Migration Path

### Existing Users
```bash
# Existing commands continue to work exactly as before:

# Minimal (default)
curl -sL URL | bash -s /path/to/target

# Full
curl -sL URL | bash -s -- /path/to/target --full

# NEW: Interactive
./install.sh /path/to/target --interactive
```

### Backward Compatibility
- All existing flags (`--minimal`, `--full`, `--dry-run`, `--force`) work unchanged
- Default behavior (piped curl → minimal) remains the same
- New `--interactive` flag is opt-in only
- No breaking changes to command-line interface

---

## 10. Future Enhancements

### Post-v1.0 Features
1. **Component Dependencies**: Auto-select dependencies (e.g., Python ADW → planning commands)
2. **Size Estimation**: Show disk space per component before installation
3. **Incremental Updates**: Add/remove components after initial install
4. **Component Profiles**: Save custom selections as named profiles
5. **Conflict Detection**: Warn about conflicting component combinations
6. **Progress Bars**: Enhanced visual feedback during installation
7. **Installation History**: Track component additions/removals over time

### Advanced Features
- **Configuration Templates**: Pre-defined templates for different project types
- **Plugin System**: Allow third-party component catalogs
- **Update Manager**: Check for and install component updates
- **Rollback Support**: Revert to previous installation state

---

## Appendix A: Full Code Integration Points

### File: `install.sh`

```bash
# Add after line 36 (after MODE definitions):
MODE_INTERACTIVE="interactive"

# Add after line 61 (color definitions):
readonly SPINNER=('⠋' '⠙' '⠹' '⠸' '⠼' '⠴' '⠦' '⠧' '⠇' '⠏')

# Insert all new functions before main() (around line 762):
# - detect_interactive_mode()
# - read_user_input()
# - init_component_state()
# - toggle_component()
# - toggle_all()
# - get_indicator()
# - count_selected()
# - show_component_menu()
# - handle_menu_selection()
# - run_interactive_menu()
# - show_installation_summary()
# - confirm_installation()
# - install_slash_command_category()
# - install_advanced_component()
# - run_component_installation()

# Update main() starting at line 765
# (See section 3.6 for complete implementation)
```

---

## Appendix B: Component File Mappings

```yaml
# Complete mapping of components to files

slash_commands:
  planning:
    - .claude/commands/planning/plan_w_docs.md
    - .claude/commands/planning/plan_w_docs_improved.md
    - .claude/commands/planning/feature.md
    - .claude/commands/planning/bug.md
    - .claude/commands/planning/chore.md
    - .claude/commands/planning/patch.md

  workflow:
    - .claude/commands/workflow/build_adw.md
    - .claude/commands/workflow/build.md
    - .claude/commands/workflow/implement.md
    - .claude/commands/workflow/scout.md
    - .claude/commands/workflow/scout_improved.md
    - .claude/commands/workflow/scout_fixed.md
    - .claude/commands/workflow/scout_parallel.md
    - .claude/commands/workflow/scout_plan_build.md
    - .claude/commands/workflow/scout_plan_build_improved.md

  git:
    - .claude/commands/git/*.md (all files)

  testing:
    - .claude/commands/testing/*.md (all files)

  session:
    - .claude/commands/session/*.md (all files)

  analysis:
    - .claude/commands/analysis/*.md (all files)

  utilities:
    - .claude/commands/utilities/*.md (all files)

advanced:
  python_adw:
    - adws/** (all files and subdirectories)

  hooks:
    - .claude/hooks/** (all files)

  skills:
    - .claude/skills/** (all files)

  scripts:
    - scripts/validate_pipeline.sh
    - scripts/workflow.sh
    - scripts/worktree_manager.sh
    - scripts/fix_agents_naming.sh
```

---

## Summary

This specification provides a complete design for an interactive installer menu system that:

1. **Works with curl piping** via `/dev/tty` stdin handling
2. **Maintains backward compatibility** with existing `--minimal` and `--full` modes
3. **Provides numbered menu** with clear categories and visual indicators
4. **Offers smart defaults** (Minimal, Standard, Full presets)
5. **Pure bash implementation** with no external dependencies
6. **Clear user experience** with progress feedback and confirmation

The implementation can be integrated into the existing `install.sh` by adding the functions from sections 3.1-3.6 and updating the main() entry point. All existing functionality is preserved while adding powerful new interactive capabilities.
