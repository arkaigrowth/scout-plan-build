#!/bin/bash
# Trace file references in .claude/commands/ folder
# v2.1: Environment-aware (Claude Code vs Web), non-invasive defaults

set -euo pipefail

# ==============================================================================
# Environment Detection & Path Configuration
# ==============================================================================

detect_environment() {
    # Detect if running in Claude Web vs Local (Claude Code CLI or terminal)
    if [ -d "/mnt/user-data/uploads" ]; then
        echo "claude_web"
    else
        echo "local"
    fi
}

configure_paths() {
    local env="$1"
    
    if [ "$env" = "claude_web" ]; then
        # Claude Web: Read-only uploads, write to outputs
        PROJECT_ROOT="/mnt/user-data/uploads"
        
        # In Claude Web, we must write to outputs directory
        OUTPUT_BASE="/mnt/user-data/outputs/dependency-traces"
    else
        # Local: Claude Code CLI or terminal
        # Detect actual project root
        PROJECT_ROOT="${PROJECT_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
        
        # Smart output directory detection (non-invasive)
        # Priority: existing scout_outputs > existing ai_docs > hidden fallback
        if [ -d "$PROJECT_ROOT/scout_outputs" ]; then
            # User's repo convention (if exists)
            OUTPUT_BASE="$PROJECT_ROOT/scout_outputs/traces"
        elif [ -d "$PROJECT_ROOT/ai_docs" ]; then
            # Alternative convention (if exists)
            OUTPUT_BASE="$PROJECT_ROOT/ai_docs/analyses/traces"
        else
            # Non-invasive default: hidden directory
            OUTPUT_BASE="$PROJECT_ROOT/.dependency-traces"
        fi
    fi
    
    echo "PROJECT_ROOT=$PROJECT_ROOT"
    echo "OUTPUT_BASE=$OUTPUT_BASE"
}

# Initialize environment
ENV=$(detect_environment)
eval $(configure_paths "$ENV")

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RUN_DIR="${OUTPUT_BASE}/${TIMESTAMP}"

# ==============================================================================
# Parse Arguments
# ==============================================================================

COMMANDS_DIR="${1:-.claude/commands}"
OUTPUT_DIR="${2:-$RUN_DIR}"
CONTEXT_MODE="${CONTEXT_MODE:-summary}"  # minimal | summary | full

# Create output directory
mkdir -p "$OUTPUT_DIR"

OUTPUT_FILE="${OUTPUT_DIR}/command_refs.json"
SUMMARY_FILE="${OUTPUT_DIR}/summary.md"

echo "🔍 Tracing file references in $COMMANDS_DIR..."
echo "🌍 Environment: $ENV"
echo "📁 Output directory: $OUTPUT_DIR"

# ==============================================================================
# Validation Checks
# ==============================================================================

if [ ! -d "$COMMANDS_DIR" ]; then
    echo "❌ Error: Directory not found: $COMMANDS_DIR"
    exit 1
fi

# Check for required tools (use ripgrep instead of grep -oP for portability)
if ! command -v rg &>/dev/null; then
    echo "⚠️  Warning: ripgrep not found. Using fallback grep (slower)."
    USE_RIPGREP=false
else
    USE_RIPGREP=true
fi

if ! command -v jq &>/dev/null; then
    echo "❌ Error: jq not found. Install via: brew install jq"
    exit 1
fi

# ==============================================================================
# Reference Extraction (Portable: ripgrep + sed fallback)
# ==============================================================================

extract_markdown_links() {
    local mdfile="$1"
    
    if $USE_RIPGREP; then
        # Use ripgrep for fast extraction
        rg -o '\[.*?\]\(([^)]+)\)' --only-matching --no-filename "$mdfile" 2>/dev/null | \
            sed 's/.*(\(.*\))/\1/' || true
    else
        # Fallback: pure sed (portable but slower)
        sed -n 's/.*\[\([^]]*\)\](\([^)]*\)).*/\2/p' "$mdfile" || true
    fi
}

extract_quoted_paths() {
    local mdfile="$1"
    
    # Extract paths in quotes/backticks: "path.py", 'path.sh', `path.js`
    if $USE_RIPGREP; then
        rg -o '["'"'"'`]([a-zA-Z0-9/_.-]+\.(sh|py|js|ts|md|json|yaml|yml))["'"'"'`]' \
            --only-matching --no-filename "$mdfile" 2>/dev/null | \
            sed 's/["'"'"'`]//g' || true
    else
        grep -o '["'"'"'`][a-zA-Z0-9/_.-]*\.\(sh\|py\|js\|ts\|md\|json\|yaml\|yml\)["'"'"'`]' "$mdfile" 2>/dev/null | \
            sed 's/["'"'"'`]//g' || true
    fi
}

# ==============================================================================
# Main Extraction Loop
# ==============================================================================

find "$COMMANDS_DIR" -name "*.md" -type f | while read -r mdfile; do
    # Extract markdown links [text](path)
    extract_markdown_links "$mdfile" | while read -r ref; do
        # Skip URLs
        if [[ "$ref" =~ ^https?:// ]] || [[ "$ref" =~ ^mailto: ]]; then
            continue
        fi
        
        # Validate file exists (check multiple locations)
        if [ -f "$COMMANDS_DIR/$ref" ] || [ -f "$PROJECT_ROOT/$ref" ] || [ -f "$ref" ]; then
            echo "{\"file\":\"$mdfile\",\"reference\":\"$ref\",\"type\":\"markdown_link\",\"status\":\"valid\"}"
        else
            echo "{\"file\":\"$mdfile\",\"reference\":\"$ref\",\"type\":\"markdown_link\",\"status\":\"broken\"}"
        fi
    done
    
    # Extract quoted paths
    extract_quoted_paths "$mdfile" | while read -r ref; do
        if [ -f "$PROJECT_ROOT/$ref" ] || [ -f "$ref" ]; then
            echo "{\"file\":\"$mdfile\",\"reference\":\"$ref\",\"type\":\"quoted_path\",\"status\":\"valid\"}"
        else
            echo "{\"file\":\"$mdfile\",\"reference\":\"$ref\",\"type\":\"quoted_path\",\"status\":\"broken\"}"
        fi
    done
done | jq -s '.' > "$OUTPUT_FILE"

# ==============================================================================
# Generate Statistics & Summary
# ==============================================================================

total=$(jq 'length' "$OUTPUT_FILE")
valid=$(jq '[.[] | select(.status=="valid")] | length' "$OUTPUT_FILE")
broken=$(jq '[.[] | select(.status=="broken")] | length' "$OUTPUT_FILE")

# Generate human-readable summary
cat > "$SUMMARY_FILE" << EOF
# File Reference Trace Summary

**Run:** $(date)
**Environment:** $ENV
**Directory:** $COMMANDS_DIR
**Output:** $OUTPUT_FILE

## Statistics

- Total references: $total
- Valid references: $valid
- Broken references: $broken

## Broken References

EOF

if [ "$broken" -gt 0 ]; then
    jq -r '.[] | select(.status=="broken") | "- `\(.file)` → `\(.reference)`"' "$OUTPUT_FILE" >> "$SUMMARY_FILE"
else
    echo "✅ No broken references found!" >> "$SUMMARY_FILE"
fi

# ==============================================================================
# Create 'latest' Symlink (only in local environment)
# ==============================================================================

if [ "$OUTPUT_DIR" = "$RUN_DIR" ] && [ "$ENV" = "local" ]; then
    LATEST_LINK="${OUTPUT_BASE}/latest"
    rm -f "$LATEST_LINK"
    ln -sf "$RUN_DIR" "$LATEST_LINK"
    echo "📌 Latest results linked at: $LATEST_LINK"
fi

# ==============================================================================
# Context-Mode Output (Token Management)
# ==============================================================================

echo ""
echo "✅ Trace complete!"
echo "📄 Full results: $OUTPUT_FILE"
echo "📋 Summary: $SUMMARY_FILE"
echo ""

case "$CONTEXT_MODE" in
    minimal)
        # MINIMAL: Just counts (100 tokens)
        echo "== MINIMAL CONTEXT MODE =="
        jq -n \
            --arg total "$total" \
            --arg valid "$valid" \
            --arg broken "$broken" \
            --arg file "$OUTPUT_FILE" \
            '{
                total: $total | tonumber,
                valid: $valid | tonumber,
                broken: $broken | tonumber,
                output_file: $file,
                message: (if ($broken | tonumber) > 0 then 
                    "Found \($broken) broken references. Read full details from output_file." 
                else 
                    "All references valid!" 
                end)
            }'
        ;;
    
    summary)
        # SUMMARY: Broken refs only (500-2000 tokens)
        echo "== SUMMARY CONTEXT MODE =="
        jq '{
            stats: {
                total: length,
                valid: [.[] | select(.status=="valid")] | length,
                broken: [.[] | select(.status=="broken")] | length
            },
            broken_references: [.[] | select(.status=="broken")],
            output_file: "'"$OUTPUT_FILE"'",
            summary_file: "'"$SUMMARY_FILE"'"
        }' "$OUTPUT_FILE"
        ;;
    
    full)
        # FULL: Everything (5000-50000 tokens) - use sparingly!
        echo "== FULL CONTEXT MODE (WARNING: High token usage) =="
        cat "$OUTPUT_FILE"
        ;;
    
    *)
        echo "❌ Unknown CONTEXT_MODE: $CONTEXT_MODE"
        echo "Valid modes: minimal, summary, full"
        exit 1
        ;;
esac

# Auto-generate ASCII diagrams if script exists
if [ -f "$SCRIPT_DIR/generate_ascii_diagrams.py" ]; then
    DIAGRAM_FILE="${OUTPUT_DIR}/diagrams.md"
    echo ""
    echo "📊 Generating ASCII diagrams..."
    if python "$SCRIPT_DIR/generate_ascii_diagrams.py" "$OUTPUT_FILE" "$DIAGRAM_FILE" 2>/dev/null; then
        echo "✅ Diagrams saved to: $DIAGRAM_FILE"
    else
        echo "⚠️  Diagram generation skipped (Python not available or error occurred)"
    fi
fi

echo ""
echo "💡 Tip: Use CONTEXT_MODE=minimal for lowest token usage"
echo "   Example: CONTEXT_MODE=minimal bash $0"
