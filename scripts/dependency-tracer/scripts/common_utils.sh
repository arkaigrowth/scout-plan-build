#!/bin/bash
# Common utilities for dependency-tracer scripts
# Provides cross-platform compatibility functions

# Universal grep function with automatic fallback
# Usage: safe_grep "pattern" "file"
safe_grep() {
    local pattern="$1"
    local file="$2"

    if command -v rg &>/dev/null; then
        # Use ripgrep (fastest, most compatible)
        rg -o "$pattern" "$file" 2>/dev/null
    elif command -v ggrep &>/dev/null; then
        # GNU grep on macOS (from brew install grep)
        ggrep -oP "$pattern" "$file" 2>/dev/null
    elif grep --version 2>/dev/null | grep -q "GNU grep"; then
        # GNU grep on Linux
        grep -oP "$pattern" "$file" 2>/dev/null
    else
        # Pure sed fallback (works everywhere but slower)
        # Note: This is a simplified pattern match, not full Perl regex
        sed -n "s/.*\($pattern\).*/\1/p" "$file" 2>/dev/null
    fi
}

# Extract markdown links [text](path)
# Usage: extract_markdown_links "file.md"
extract_markdown_links() {
    local file="$1"

    if command -v rg &>/dev/null; then
        # Ripgrep with proper capture group
        rg -o '\[([^\]]*)\]\(([^)]+)\)' --only-matching -r '$2' "$file" 2>/dev/null | \
            grep -v '^https\?://'
    else
        # Fallback to sed
        sed -n 's/.*\[\([^]]*\)\](\([^)]*\)).*/\2/p' "$file" 2>/dev/null | \
            grep -v '^https\?://'
    fi
}

# Extract quoted file paths
# Usage: extract_quoted_paths "file"
extract_quoted_paths() {
    local file="$1"

    if command -v rg &>/dev/null; then
        # Ripgrep for quoted paths with file extensions
        rg -o '["'"'"'`]([a-zA-Z0-9/_.-]+\.(sh|py|js|ts|md|json|yaml|yml))["'"'"'`]' \
           --only-matching -r '$1' "$file" 2>/dev/null
    else
        # Fallback to grep/sed combination
        grep -o '["'"'"'`][a-zA-Z0-9/_.-]*\.\(sh\|py\|js\|ts\|md\|json\|yaml\|yml\)["'"'"'`]' "$file" 2>/dev/null | \
            sed 's/["'"'"'`]//g'
    fi
}

# Validate JSON file
# Usage: validate_json "file.json"
validate_json() {
    local file="$1"

    if ! jq empty "$file" 2>/dev/null; then
        echo "❌ Invalid JSON in $file" >&2

        # Try to diagnose the issue with Python
        python3 -c "
import json, sys
try:
    with open('$file') as f:
        json.load(f)
    print('✅ JSON is valid')
except json.JSONDecodeError as e:
    print(f'❌ JSON error at line {e.lineno}, column {e.colno}: {e.msg}', file=sys.stderr)
    sys.exit(1)
        " 2>&1
        return $?
    fi
    return 0
}

# Create pointer file instead of symlink (works everywhere)
# Usage: create_pointer "target_dir" "pointer_file"
create_pointer() {
    local target="$1"
    local pointer="$2"

    echo "$target" > "$pointer"
    echo "📍 Created pointer: $pointer -> $target"
}

# Read pointer file
# Usage: read_pointer "pointer_file"
read_pointer() {
    local pointer="$1"

    if [ -f "$pointer" ]; then
        cat "$pointer"
    else
        echo ""
        return 1
    fi
}

# Check if running on macOS
is_macos() {
    [[ "$OSTYPE" == "darwin"* ]]
}

# Check if running in Claude Web environment
is_claude_web() {
    [ -d "/mnt/user-data/uploads" ]
}

# Print diagnostic info
print_env_info() {
    echo "🔍 Environment Diagnostics:"
    echo "  OS: $OSTYPE"

    if is_macos; then
        echo "  Platform: macOS"
    elif is_claude_web; then
        echo "  Platform: Claude Web"
    else
        echo "  Platform: Linux/Other"
    fi

    echo "  Available tools:"
    command -v rg &>/dev/null && echo "    ✅ ripgrep (rg)"
    command -v ggrep &>/dev/null && echo "    ✅ GNU grep (ggrep)"
    command -v ast-grep &>/dev/null && echo "    ✅ ast-grep"
    command -v jq &>/dev/null && echo "    ✅ jq"
    command -v python3 &>/dev/null && echo "    ✅ python3"
}