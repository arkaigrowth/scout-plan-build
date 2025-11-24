#!/bin/bash
# Fix Conversation (Subagent)-Optimized Dependency Tracer Wrapper
# v2.1: Updated terminology, environment-aware

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Detect environment
if [ -d "/mnt/user-data/uploads" ]; then
    ENV="claude_web"
    PROJECT_ROOT="/mnt/user-data/uploads"
else
    ENV="local"
    PROJECT_ROOT="${PROJECT_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
fi

# ==============================================================================
# Configuration
# ==============================================================================

TRACE_COMMANDS="${TRACE_COMMANDS:-true}"
TRACE_PYTHON="${TRACE_PYTHON:-true}"
COMMANDS_DIR="${COMMANDS_DIR:-.claude/commands}"
PYTHON_DIR="${PYTHON_DIR:-adws}"

# Force minimal context mode for wrapper
export CONTEXT_MODE=minimal

echo "🤖 Dependency Tracer - Fix Conversation (Subagent)-Optimized Workflow"
echo "======================================================================="
echo "🌍 Environment: $ENV"
echo ""

# ==============================================================================
# Phase 1: Run Traces (Deterministic, 0 tokens)
# ==============================================================================

echo "Phase 1: Running deterministic traces..."
echo ""

TRACE_OUTPUTS=()

if [ "$TRACE_COMMANDS" = "true" ] && [ -d "$COMMANDS_DIR" ]; then
    echo "  → Tracing command file references..."
    CMD_OUTPUT=$("$SCRIPT_DIR/trace_command_refs.sh" "$COMMANDS_DIR" 2>&1)
    CMD_JSON=$(echo "$CMD_OUTPUT" | grep -A 100 "== MINIMAL CONTEXT MODE ==" | tail -n +2)
    TRACE_OUTPUTS+=("$CMD_JSON")
fi

if [ "$TRACE_PYTHON" = "true" ] && [ -d "$PYTHON_DIR" ]; then
    echo "  → Tracing Python imports..."
    PY_OUTPUT=$("$SCRIPT_DIR/trace_python_imports.sh" "$PYTHON_DIR" 2>&1)
    PY_JSON=$(echo "$PY_OUTPUT" | grep -A 100 "== MINIMAL CONTEXT MODE ==" | tail -n +2)
    TRACE_OUTPUTS+=("$PY_JSON")
fi

echo ""
echo "✅ Traces complete (0 tokens consumed)"
echo ""

# ==============================================================================
# Phase 2: Aggregate Results (Minimal Context)
# ==============================================================================

echo "Phase 2: Aggregating results..."
echo ""

# Combine all trace outputs
COMBINED_STATS=$(cat <<EOF
{
  "traces": [
$(IFS=,; echo "${TRACE_OUTPUTS[*]}")
  ],
  "workflow": "fix-conversation-subagent-optimized",
  "instructions": {
    "main_conversation": "Read this summary ONLY. Do NOT read full JSON files.",
    "spawn_fix_conversations": "For each broken reference, spawn a fix conversation (subagent) that reads ONE entry from the full file and suggests a fix.",
    "pattern": "Main context: ~100 tokens. Each fix conversation (subagent): ~300 tokens. Total: 100 + (N × 300) instead of 50K+"
  }
}
EOF
)

echo "$COMBINED_STATS" | jq '.'

echo ""
echo "======================================================================="
echo ""
echo "📊 MAIN CONVERSATION SUMMARY (100 tokens):"
echo ""

# Extract key metrics
total_broken=$(echo "$COMBINED_STATS" | jq '[.traces[].broken] | add')
total_valid=$(echo "$COMBINED_STATS" | jq '[.traces[].valid] | add')

echo "  Total valid: $total_valid"
echo "  Total broken: $total_broken"
echo ""

if [ "$total_broken" -gt 0 ]; then
    echo "🔧 FIX CONVERSATION (SUBAGENT) WORKFLOW:"
    echo ""
    echo "  For each broken reference:"
    echo "    1. Spawn fix conversation (subagent) with SINGLE broken reference context"
    echo "    2. Fix conversation (subagent) reads full details from output_file"
    echo "    3. Fix conversation (subagent) suggests fix"
    echo "    4. Fix conversation (subagent) writes fix to traces/latest/fixes/{ref_hash}.md"
    echo ""
    echo "  Token efficiency:"
    echo "    - Main context: 100 tokens (this summary)"
    echo "    - Each fix conversation (subagent): 300 tokens (one reference + fix)"
    echo "    - Total: 100 + ($total_broken × 300) = $((100 + total_broken * 300)) tokens"
    echo ""
    echo "  vs Traditional approach: 50,000+ tokens (full JSON in context)"
    echo ""
    echo "📂 Full details available in:"
    
    echo "$COMBINED_STATS" | jq -r '.traces[].output_file' | while read -r file; do
        echo "    - $file"
    done
    
    echo "$COMBINED_STATS" | jq -r '.traces[].summary_file' | while read -r file; do
        echo "    - $file"
    done
else
    echo "✅ No broken references found. No fix conversations (subagents) needed."
fi

echo ""
echo "======================================================================="
echo ""
echo "💡 NEXT STEPS:"
echo ""
echo "  Option A: Read summary files and triage manually"
if [ "$ENV" = "local" ]; then
    echo "    → cat scout_outputs/traces/latest/summary.md"
else
    echo "    → cat /mnt/user-data/outputs/dependency-traces/latest/summary.md"
fi
echo ""
echo "  Option B: Spawn fix conversations (subagents) - one per broken ref"
echo "    → Each fix conversation (subagent) reads ONE entry, suggests fix, writes to fixes/"
echo ""
echo "  Option C: Generate comprehensive report"
echo "    → Build dependency graph, analyze impact, prioritize fixes"
echo ""
