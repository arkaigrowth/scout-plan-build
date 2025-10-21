#!/bin/bash
# worktree_manager.sh - Git Worktree Management System
# Version: 1.0.0
# Purpose: Manage git worktrees for parallel development and undo/redo

set -euo pipefail

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

WORKTREE_DIR="worktrees"
CHECKPOINT_INTERVAL="${CHECKPOINT_INTERVAL:-300}"  # 5 minutes
MAX_CHECKPOINTS="${MAX_CHECKPOINTS:-50}"
ARCHIVE_DIR=".worktree-archive"

# ═══════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

error() {
    echo "❌ Error: $*" >&2
    return 1
}

warning() {
    echo "⚠️  Warning: $*" >&2
}

success() {
    echo "✅ $*"
}

info() {
    echo "💡 $*"
}

validate_name() {
    local name="$1"
    [[ "$name" =~ ^[a-z0-9-]+$ ]] || error "Invalid name: use kebab-case (a-z, 0-9, -)"
}

# ═══════════════════════════════════════════════════════════════════════════
# CORE WORKTREE OPERATIONS
# ═══════════════════════════════════════════════════════════════════════════

worktree_create() {
    local name="$1"
    local base="${2:-main}"
    local worktree_path="$WORKTREE_DIR/$name"
    local branch_name="feature/$name"

    # Validation
    validate_name "$name"
    [[ -d "$worktree_path" ]] && error "Worktree already exists: $name"
    git rev-parse --verify "$base" &>/dev/null || error "Base branch not found: $base"

    # Create worktree
    mkdir -p "$WORKTREE_DIR"
    git worktree add -b "$branch_name" "$worktree_path" "$base" || error "Failed to create worktree"

    # Initialize checkpoint system
    cd "$worktree_path"

    # Create metadata
    cat > .worktree-meta.json <<EOF
{
  "name": "$name",
  "created": "$(date -Iseconds)",
  "base_branch": "$base",
  "auto_checkpoint": true,
  "checkpoint_interval": $CHECKPOINT_INTERVAL,
  "checkpoints": []
}
EOF

    echo "# Checkpoint History for $name" > .checkpoint-history
    echo "Created: $(date -Iseconds)" >> .checkpoint-history
    touch .git/REDO_STACK

    # Pre-commit hook
    mkdir -p .git/hooks
    cat > .git/hooks/pre-commit <<'HOOK'
#!/bin/bash
if [[ -f .worktree-meta.json ]]; then
    timestamp=$(date -Iseconds)
    checkpoint_count=$(git log --oneline --grep='^wip-' | wc -l)
    echo "Checkpoint $(($checkpoint_count + 1)): $timestamp" >> .checkpoint-history
fi
HOOK
    chmod +x .git/hooks/pre-commit

    # Initial checkpoint
    git add .worktree-meta.json .checkpoint-history .git/REDO_STACK
    git commit -m "wip-$(date +%s): Initialize worktree $name" \
        --author="Worktree Init <noreply@worktree>"

    success "Worktree created: $worktree_path"
    echo "   Branch: $branch_name"
    echo "   Base: $base"
    echo "   Auto-checkpoint: enabled"
}

worktree_checkpoint() {
    local message="${1:-auto-checkpoint}"
    local timestamp=$(date +%s)
    local checkpoint_name="wip-$timestamp"

    # Check for changes
    git diff-index --quiet HEAD -- 2>/dev/null && {
        warning "No changes to checkpoint"
        return 0
    }

    # Clear redo stack
    [[ -f .git/REDO_STACK ]] && > .git/REDO_STACK

    # Stage and commit
    git add -A
    local stats=$(git diff --cached --stat | tail -1)

    git commit -m "$checkpoint_name: $message" \
        --author="Worktree Checkpoint <noreply@worktree>" || error "Failed to create checkpoint"

    local hash=$(git rev-parse HEAD)
    local short_hash="${hash:0:12}"

    # Update history
    [[ -f .checkpoint-history ]] && {
        echo "Checkpoint: $checkpoint_name ($short_hash)" >> .checkpoint-history
        echo "  Time: $(date -Iseconds)" >> .checkpoint-history
        echo "  Message: $message" >> .checkpoint-history
        echo "  Changes: $stats" >> .checkpoint-history
        echo "" >> .checkpoint-history
    }

    cleanup_old_checkpoints

    success "Checkpoint created: $checkpoint_name"
    echo "   Hash: $short_hash"
    echo "   Changes: $stats"
}

worktree_undo() {
    local n="${1:-1}"

    # Validation
    [[ "$n" =~ ^[0-9]+$ ]] || error "Invalid count: must be positive integer"
    [[ $n -gt 50 ]] && error "Safety limit: max 50 undos"

    local commit_count=$(git rev-list --count HEAD)
    [[ $n -ge $commit_count ]] && error "Cannot undo $n commits (only $commit_count available)"

    local current=$(git rev-parse HEAD)
    local target=$(git rev-parse "HEAD~$n") || error "Target commit not found"

    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        warning "Uncommitted changes detected"
        git status --short
        read -p "Stash changes and continue? (y/N): " confirm
        [[ "$confirm" == "y" ]] && {
            git stash push -m "auto-stash before undo"
            success "Changes stashed"
        } || {
            echo "Undo cancelled"
            return 0
        }
    fi

    # Store in redo stack
    echo "$current" >> .git/REDO_STACK

    # Perform undo
    git reset --hard "$target" || {
        sed -i '' '$d' .git/REDO_STACK 2>/dev/null
        error "Reset failed"
    }

    success "Undone $n checkpoint(s)"
    echo "   From: ${current:0:12}"
    echo "   To:   ${target:0:12}"
}

worktree_redo() {
    local redo_stack=".git/REDO_STACK"

    [[ ! -f "$redo_stack" ]] && error "No redo available"

    local target=$(tail -n 1 "$redo_stack")
    [[ -z "$target" ]] && error "Redo stack is empty"

    git rev-parse "$target" &>/dev/null || {
        sed -i '' '$d' "$redo_stack"
        error "Redo target no longer exists"
    }

    git reset --hard "$target"
    sed -i '' '$d' "$redo_stack"

    success "Redone to checkpoint: ${target:0:12}"
}

worktree_switch() {
    local name="$1"
    local target="$WORKTREE_DIR/$name"

    [[ ! -d "$target" ]] && {
        error "Worktree not found: $name"
        echo ""
        echo "Available worktrees:"
        git worktree list
        return 1
    }

    # Auto-checkpoint current location
    if git rev-parse --git-dir &>/dev/null 2>&1; then
        info "Auto-checkpointing current worktree..."
        worktree_checkpoint "auto-save before switch" 2>/dev/null || true
    fi

    cd "$target"

    local branch=$(git branch --show-current)
    local checkpoint_count=$(git log --oneline --grep='^wip-' | wc -l)
    local last_checkpoint=$(git log -1 --format='%cr' --grep='^wip-')

    success "Switched to worktree: $name"
    echo "   Branch: $branch"
    echo "   Checkpoints: $checkpoint_count available"
    echo "   Last checkpoint: $last_checkpoint"
}

worktree_list() {
    echo "📋 Active Worktrees:"
    echo ""

    git worktree list --porcelain | awk '
    /^worktree/ { wt = $2 }
    /^branch/ { br = $2; sub(/^refs\/heads\//, "", br) }
    /^$/ {
        if (wt && br) {
            cmd = "cd " wt " && git log -1 --format=\"%cr\" --grep=\"^wip-\" 2>/dev/null"
            cmd | getline last_cp
            close(cmd)

            cmd = "cd " wt " && git log --oneline --grep=\"^wip-\" | wc -l"
            cmd | getline cp_count
            close(cmd)

            printf "  • %s\n", wt
            printf "    Branch: %s\n", br
            printf "    Checkpoints: %s\n", (cp_count > 0 ? cp_count : "none")
            printf "    Last: %s\n\n", (last_cp ? last_cp : "never")
        }
        wt = ""; br = ""
    }'
}

worktree_diff() {
    local other_name="$1"
    local current_branch=$(git branch --show-current)
    local current_name=$(basename "$PWD")
    local other_path="../$other_name"

    [[ ! -d "$other_path" ]] && error "Worktree not found: $other_name"

    local other_branch=$(cd "$other_path" && git branch --show-current)

    # Check for conflicts
    git merge-tree $(git merge-base HEAD "$other_path/HEAD") HEAD "$other_path/HEAD" > /tmp/merge-preview 2>/dev/null
    local conflicts=$(grep -c '^<<<<<<<' /tmp/merge-preview 2>/dev/null || echo 0)

    echo "📊 Diff between worktrees:"
    echo "   Current: $current_branch ($current_name)"
    echo "   Other:   $other_branch ($other_name)"
    echo ""

    if [[ $conflicts -gt 0 ]]; then
        warning "Conflicts: $conflicts file(s) would conflict"
    else
        success "Conflicts: None"
    fi

    local stats=$(git diff --stat "$other_branch" 2>/dev/null)
    echo "   $stats"
}

worktree_merge() {
    local worktree_name="$1"
    local target_branch="${2:-main}"
    local worktree_path="$WORKTREE_DIR/$worktree_name"

    [[ ! -d "$worktree_path" ]] && error "Worktree not found: $worktree_name"

    local source_branch=$(cd "$worktree_path" && git branch --show-current)

    # Check for uncommitted changes
    (cd "$worktree_path" && git diff-index --quiet HEAD --) || {
        error "Worktree has uncommitted changes. Checkpoint first: cd $worktree_path && worktree_checkpoint"
    }

    # Check for conflicts
    local merge_base=$(git merge-base "$target_branch" "$source_branch")
    git merge-tree "$merge_base" "$target_branch" "$source_branch" > /tmp/merge-preview 2>/dev/null

    if grep -q '^<<<<<<<' /tmp/merge-preview; then
        warning "Merge will have conflicts!"
        cat /tmp/merge-preview
        return 1
    fi

    # Checkpoint before merge
    worktree_checkpoint "pre-merge checkpoint"

    # Perform merge
    git checkout "$target_branch" || error "Failed to checkout $target_branch"

    info "Merging $source_branch → $target_branch..."
    git merge --no-ff "$source_branch" -m "Merge worktree: $worktree_name" || {
        git merge --abort
        error "Merge failed"
    }

    success "Merged worktree: $worktree_name → $target_branch"
    info "Cleanup: worktree_cleanup $worktree_name"
}

worktree_cleanup() {
    local name="$1"
    local force="${2:-false}"
    local worktree_path="$WORKTREE_DIR/$name"

    [[ ! -d "$worktree_path" ]] && error "Worktree not found: $name"

    local branch=$(cd "$worktree_path" && git branch --show-current)

    # Check if merged (unless force)
    if [[ "$force" != "true" ]]; then
        git branch --merged main | grep -q "$branch" || {
            warning "Branch not merged to main"
            echo "   Force cleanup: worktree_cleanup $name true"
            return 1
        }
    fi

    # Archive metadata
    mkdir -p "$ARCHIVE_DIR"
    [[ -f "$worktree_path/.worktree-meta.json" ]] && {
        cp "$worktree_path/.worktree-meta.json" \
           "$ARCHIVE_DIR/${name}-$(date +%s).json"
    }

    # Remove worktree
    git worktree remove "$worktree_path" || error "Failed to remove worktree"

    # Delete branch
    git branch -d "$branch" 2>/dev/null || warning "Branch $branch still has references"

    success "Cleaned up worktree: $name"
    echo "   Metadata: Archived to $ARCHIVE_DIR/"
}

cleanup_old_checkpoints() {
    local checkpoint_count=$(git log --oneline --grep='^wip-' | wc -l)

    if [[ $checkpoint_count -gt $MAX_CHECKPOINTS ]]; then
        info "Cleaning up old checkpoints..."

        local old_checkpoints=$(git log --oneline --grep='^wip-' --format='%H' | tail -n +$((MAX_CHECKPOINTS + 1)))

        mkdir -p .checkpoint-archive

        echo "$old_checkpoints" | while read commit; do
            # Skip tagged commits
            git tag --points-at "$commit" | grep -q . && continue

            # Skip merged commits
            git branch --contains "$commit" | grep -q main && continue

            # Archive
            local short="${commit:0:12}"
            git show --stat "$commit" > ".checkpoint-archive/$short.txt" 2>/dev/null || true
        done
    fi
}

# ═══════════════════════════════════════════════════════════════════════════
# AUTO-CHECKPOINT DAEMON
# ═══════════════════════════════════════════════════════════════════════════

auto_checkpoint_daemon() {
    local worktree_path="${1:-.}"

    cd "$worktree_path" || error "Invalid worktree path: $worktree_path"

    echo "🤖 Auto-checkpoint daemon started"
    echo "   Interval: ${CHECKPOINT_INTERVAL}s"
    echo "   Worktree: $worktree_path"
    echo ""

    while true; do
        sleep "$CHECKPOINT_INTERVAL"

        [[ ! -f .worktree-meta.json ]] && {
            warning "Worktree removed, stopping daemon"
            exit 0
        }

        # Check auto-checkpoint enabled
        if command -v jq &>/dev/null; then
            local enabled=$(jq -r '.auto_checkpoint' .worktree-meta.json 2>/dev/null)
            [[ "$enabled" != "true" ]] && continue
        fi

        # Check for changes
        git diff-index --quiet HEAD -- && continue

        # Create checkpoint
        timestamp=$(date +%s)
        git add -A
        git commit -m "wip-$timestamp: auto-checkpoint" \
            --author="Auto-Checkpoint <noreply@worktree>" &>/dev/null

        echo "💾 Auto-checkpoint: wip-$timestamp ($(date '+%Y-%m-%d %H:%M:%S'))"
    done
}

# ═══════════════════════════════════════════════════════════════════════════
# PARALLEL EXECUTION
# ═══════════════════════════════════════════════════════════════════════════

parallel_build() {
    local spec_files=("$@")
    local pids=()

    echo "🚀 Starting parallel builds..."
    echo "   Tasks: ${#spec_files[@]}"
    echo ""

    for spec in "${spec_files[@]}"; do
        local issue_num=$(basename "$spec" | grep -oE '[0-9]+' | head -1)
        local worktree_name="build-issue-$issue_num"

        # Create worktree
        worktree_create "$worktree_name" main

        # Launch build in background
        (
            cd "$WORKTREE_DIR/$worktree_name"
            /build_adw "$spec"
            worktree_checkpoint "build complete: $spec"
        ) &

        pids+=($!)
    done

    # Wait for all builds
    echo "⏳ Waiting for builds to complete..."
    for pid in "${pids[@]}"; do
        wait "$pid"
    done

    success "All parallel builds complete"
}

# ═══════════════════════════════════════════════════════════════════════════
# CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════

usage() {
    cat <<EOF
Git Worktree Manager - v1.0.0

Usage: $0 <command> [options]

Core Commands:
  create <name> [base]       Create new worktree
  checkpoint [message]       Create undo point
  undo [n]                   Undo n checkpoints (default: 1)
  redo                       Redo last undo
  switch <name>              Switch to worktree
  list                       List all worktrees
  diff <other-worktree>      Compare with another worktree
  merge <name> [target]      Merge worktree to target branch
  cleanup <name> [force]     Remove worktree

Advanced Commands:
  auto-daemon [path]         Start auto-checkpoint daemon
  parallel-build <specs...>  Build multiple specs in parallel

Examples:
  $0 create feature-oauth main
  $0 checkpoint "implement auth flow"
  $0 undo 3
  $0 switch feature-oauth
  $0 merge feature-oauth main
  $0 cleanup feature-oauth

Environment Variables:
  CHECKPOINT_INTERVAL    Auto-checkpoint interval (default: 300s)
  MAX_CHECKPOINTS        Max checkpoints to keep (default: 50)

Documentation:
  ai_docs/architecture/GIT_WORKTREE_UNDO_SYSTEM.md
EOF
}

main() {
    local command="${1:-}"
    shift || true

    case "$command" in
        create)
            worktree_create "$@"
            ;;
        checkpoint)
            worktree_checkpoint "$@"
            ;;
        undo)
            worktree_undo "$@"
            ;;
        redo)
            worktree_redo
            ;;
        switch)
            worktree_switch "$@"
            ;;
        list)
            worktree_list
            ;;
        diff)
            worktree_diff "$@"
            ;;
        merge)
            worktree_merge "$@"
            ;;
        cleanup)
            worktree_cleanup "$@"
            ;;
        auto-daemon)
            auto_checkpoint_daemon "$@"
            ;;
        parallel-build)
            parallel_build "$@"
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            echo "Unknown command: $command"
            echo ""
            usage
            exit 1
            ;;
    esac
}

# Execute if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
