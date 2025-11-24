#!/bin/bash
# Trace Python imports in adws/ folder
# v2.1: Environment-aware, non-invasive defaults, jq bug fixed

set -euo pipefail

# ==============================================================================
# Environment Detection & Path Configuration
# ==============================================================================

detect_environment() {
    if [ -d "/mnt/user-data/uploads" ]; then
        echo "claude_web"
    else
        echo "local"
    fi
}

configure_paths() {
    local env="$1"
    
    if [ "$env" = "claude_web" ]; then
        PROJECT_ROOT="/mnt/user-data/uploads"
        OUTPUT_BASE="/mnt/user-data/outputs/dependency-traces"
    else
        PROJECT_ROOT="${PROJECT_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
        
        # Smart output directory (non-invasive)
        if [ -d "$PROJECT_ROOT/scout_outputs" ]; then
            OUTPUT_BASE="$PROJECT_ROOT/scout_outputs/traces"
        elif [ -d "$PROJECT_ROOT/ai_docs" ]; then
            OUTPUT_BASE="$PROJECT_ROOT/ai_docs/analyses/traces"
        else
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

PYTHON_DIR="${1:-adws}"
OUTPUT_DIR="${2:-$RUN_DIR}"
CONTEXT_MODE="${CONTEXT_MODE:-summary}"  # minimal | summary | full

# Create output directory
mkdir -p "$OUTPUT_DIR"

OUTPUT_FILE="${OUTPUT_DIR}/python_imports.json"
SUMMARY_FILE="${OUTPUT_DIR}/summary.md"
TEMP_DIR="/tmp/dep-tracer-$$"
mkdir -p "$TEMP_DIR"

# Cleanup temp on exit
trap "rm -rf $TEMP_DIR" EXIT

echo "🔍 Tracing Python imports in $PYTHON_DIR..."
echo "🌍 Environment: $ENV"
echo "📁 Output directory: $OUTPUT_DIR"

# ==============================================================================
# Validation Checks
# ==============================================================================

if [ ! -d "$PYTHON_DIR" ]; then
    echo "❌ Error: Directory not found: $PYTHON_DIR"
    exit 1
fi

# Check for ast-grep
if ! command -v ast-grep &>/dev/null; then
    echo "❌ Error: ast-grep not found. Install via: brew install ast-grep"
    exit 1
fi

# Check for jq
if ! command -v jq &>/dev/null; then
    echo "❌ Error: jq not found. Install via: brew install jq"
    exit 1
fi

# Check for Python
if ! command -v python3 &>/dev/null; then
    echo "❌ Error: python3 not found"
    exit 1
fi

# ==============================================================================
# Extract Imports with ast-grep
# ==============================================================================

echo "📝 Extracting imports with ast-grep..."

{
    # Pattern 1: import module
    ast-grep --pattern 'import $MODULE' "$PYTHON_DIR" --json 2>/dev/null | \
        jq -c '.[] | {
            file: .file,
            module: .metaVariables.single.MODULE.text,
            type: "import",
            line: .range.start.line
        }' 2>/dev/null || true
    
    # Pattern 2: from module import name
    ast-grep --pattern 'from $MODULE import $NAME' "$PYTHON_DIR" --json 2>/dev/null | \
        jq -c '.[] | {
            file: .file,
            module: .metaVariables.single.MODULE.text,
            name: .metaVariables.single.NAME.text,
            type: "from_import",
            line: .range.start.line
        }' 2>/dev/null || true
} | jq -s '.' > "$TEMP_DIR/imports_raw.json"

# ==============================================================================
# Validate Each Unique Module
# ==============================================================================

echo "✅ Validating modules..."

jq -r '[.[].module] | unique[]' "$TEMP_DIR/imports_raw.json" | while read -r module; do
    # Skip empty modules
    if [ -z "$module" ]; then
        continue
    fi
    
    # Try to import in Python
    if python3 -c "import $module" 2>/dev/null; then
        echo "{\"module\":\"$module\",\"status\":\"valid\",\"location\":\"installed\"}"
    else
        # Check if it's a local file (convert dots to slashes)
        module_file="${PYTHON_DIR}/${module//.//}.py"
        module_init="${PYTHON_DIR}/${module//.//}/__init__.py"
        
        if [ -f "$module_file" ] || [ -f "$module_init" ]; then
            echo "{\"module\":\"$module\",\"status\":\"valid\",\"location\":\"local\"}"
        else
            echo "{\"module\":\"$module\",\"status\":\"broken\"}"
        fi
    fi
done | jq -s '.' > "$TEMP_DIR/module_status.json"

# ==============================================================================
# Combine Results (FIXED: Proper jq join logic)
# ==============================================================================

# FIXED v2.1: Use proper variable reference in select()
jq -s '
    .[0] as $imports |
    .[1] as $status |
    $imports | map(
        . as $imp |
        . + (
            $status | 
            map(select(.module == $imp.module)) | 
            .[0] // {status: "unknown"}
        )
    )
' "$TEMP_DIR/imports_raw.json" "$TEMP_DIR/module_status.json" > "$OUTPUT_FILE"

# ==============================================================================
# Generate Statistics & Summary
# ==============================================================================

total=$(jq 'length' "$OUTPUT_FILE")
valid=$(jq '[.[] | select(.status=="valid")] | length' "$OUTPUT_FILE")
broken=$(jq '[.[] | select(.status=="broken")] | length' "$OUTPUT_FILE")
local_imports=$(jq '[.[] | select(.location=="local")] | length' "$OUTPUT_FILE")
installed_imports=$(jq '[.[] | select(.location=="installed")] | length' "$OUTPUT_FILE")

# Generate human-readable summary
cat > "$SUMMARY_FILE" << EOF
# Python Import Trace Summary

**Run:** $(date)
**Environment:** $ENV
**Directory:** $PYTHON_DIR
**Output:** $OUTPUT_FILE

## Statistics

- Total imports: $total
- Valid imports: $valid
  - Installed packages: $installed_imports
  - Local modules: $local_imports
- Broken imports: $broken

## Broken Imports

EOF

if [ "$broken" -gt 0 ]; then
    jq -r '.[] | select(.status=="broken") | 
        "- `\(.file):\(.line)` → `\(.module)` (type: \(.type))"' "$OUTPUT_FILE" >> "$SUMMARY_FILE"
    
    echo "" >> "$SUMMARY_FILE"
    echo "## Suggested Fixes" >> "$SUMMARY_FILE"
    echo "" >> "$SUMMARY_FILE"
    
    # Group by module for fix suggestions
    jq -r '[.[] | select(.status=="broken") | .module] | unique[]' "$OUTPUT_FILE" | while read -r module; do
        echo "### \`$module\`" >> "$SUMMARY_FILE"
        echo "" >> "$SUMMARY_FILE"
        echo "**Files using this module:**" >> "$SUMMARY_FILE"
        jq -r --arg mod "$module" \
            '.[] | select(.module==$mod and .status=="broken") | "- \(.file):\(.line)"' \
            "$OUTPUT_FILE" >> "$SUMMARY_FILE"
        echo "" >> "$SUMMARY_FILE"
        echo "**Possible fix:**" >> "$SUMMARY_FILE"
        echo '```bash' >> "$SUMMARY_FILE"
        echo "pip install $module --break-system-packages" >> "$SUMMARY_FILE"
        echo "# or add to requirements.txt" >> "$SUMMARY_FILE"
        echo '```' >> "$SUMMARY_FILE"
        echo "" >> "$SUMMARY_FILE"
    done
else
    echo "✅ No broken imports found!" >> "$SUMMARY_FILE"
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
            --arg summary "$SUMMARY_FILE" \
            '{
                total: $total | tonumber,
                valid: $valid | tonumber,
                broken: $broken | tonumber,
                output_file: $file,
                summary_file: $summary,
                message: (if ($broken | tonumber) > 0 then 
                    "Found \($broken) broken imports. Read summary_file for details." 
                else 
                    "All imports valid!" 
                end)
            }'
        ;;
    
    summary)
        # SUMMARY: Broken imports only (500-2000 tokens)
        echo "== SUMMARY CONTEXT MODE =="
        jq '{
            stats: {
                total: length,
                valid: [.[] | select(.status=="valid")] | length,
                broken: [.[] | select(.status=="broken")] | length,
                local: [.[] | select(.location=="local")] | length,
                installed: [.[] | select(.location=="installed")] | length
            },
            broken_imports: [
                .[] | 
                select(.status=="broken") | 
                {file, line, module, type}
            ],
            broken_modules: [.[] | select(.status=="broken") | .module] | unique,
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

echo ""
echo "💡 Tip: Use CONTEXT_MODE=minimal for lowest token usage"
echo "   Example: CONTEXT_MODE=minimal bash $0"
