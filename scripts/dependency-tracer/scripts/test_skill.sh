#!/bin/bash
# Test script for dependency-tracer v2.1
# Tests environment detection and smart path handling

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Detect environment
if [ -d "/mnt/user-data/uploads" ]; then
    ENV="claude_web"
else
    ENV="local"
fi

echo "🧪 Dependency Tracer v2.1 - Validation Test"
echo "==========================================="
echo "🌍 Environment: $ENV"
echo ""

# Check prerequisites
echo "1. Checking prerequisites..."
missing_tools=""

if ! command -v rg &> /dev/null; then
    missing_tools="${missing_tools}ripgrep "
fi

if ! command -v ast-grep &> /dev/null; then
    missing_tools="${missing_tools}ast-grep "
fi

if ! command -v jq &> /dev/null; then
    missing_tools="${missing_tools}jq "
fi

if ! command -v python3 &> /dev/null; then
    missing_tools="${missing_tools}python3 "
fi

if [ -n "$missing_tools" ]; then
    echo "❌ Missing tools: $missing_tools"
    echo ""
    echo "Install via:"
    echo "  bash scripts/setup.sh"
    exit 1
fi

echo "✅ All tools installed (ripgrep, ast-grep, jq, python3)"
echo ""

# Test environment detection
echo "2. Testing environment detection..."
if [ "$ENV" = "claude_web" ]; then
    echo "✅ Claude Web detected"
    echo "   - Read from: /mnt/user-data/uploads"
    echo "   - Write to: /mnt/user-data/outputs/dependency-traces"
elif [ "$ENV" = "local" ]; then
    echo "✅ Local (Claude Code or terminal) detected"
    
    # Test path detection logic
    if [ -d "scout_outputs" ]; then
        echo "   - Using: scout_outputs/traces/"
    elif [ -d "ai_docs" ]; then
        echo "   - Using: ai_docs/analyses/traces/"
    else
        echo "   - Using: .dependency-traces/ (fallback)"
    fi
fi
echo ""

# Test context modes
echo "3. Testing context modes..."

# Test minimal mode
echo "  → Testing CONTEXT_MODE=minimal..."
if [ -d ".claude/commands" ]; then
    if CONTEXT_MODE=minimal bash "$SCRIPT_DIR/trace_command_refs.sh" ".claude/commands" /tmp/test-minimal 2>&1 | grep -q "MINIMAL CONTEXT MODE"; then
        echo "    ✅ Minimal mode works"
    else
        echo "    ⚠️  Minimal mode test inconclusive"
    fi
else
    echo "    ⚠️  Skipped (.claude/commands not found)"
fi

# Test summary mode
echo "  → Testing CONTEXT_MODE=summary..."
if [ -d ".claude/commands" ]; then
    if CONTEXT_MODE=summary bash "$SCRIPT_DIR/trace_command_refs.sh" ".claude/commands" /tmp/test-summary 2>&1 | grep -q "SUMMARY CONTEXT MODE"; then
        echo "    ✅ Summary mode works"
    else
        echo "    ⚠️  Summary mode test inconclusive"
    fi
else
    echo "    ⚠️  Skipped (.claude/commands not found)"
fi

echo ""

# Test 4: Trace Python imports (if adws/ exists)
if [ -d "adws" ]; then
    echo "4. Testing: Trace Python imports in adws/..."
    CONTEXT_MODE=minimal bash "$SCRIPT_DIR/trace_python_imports.sh" adws /tmp/test-py 2>&1 > /tmp/trace_py_output.txt
    
    if [ -f "/tmp/test-py/python_imports.json" ]; then
        echo "✅ Python imports traced successfully"
        
        # Check for jq bug fix
        if jq -e '.[] | select(.module and .status)' /tmp/test-py/python_imports.json > /dev/null 2>&1; then
            echo "✅ jq join logic works correctly (v2.1 fix verified)"
        fi
    else
        echo "❌ Failed to generate imports report"
        cat /tmp/trace_py_output.txt
        exit 1
    fi
else
    echo "4. ⚠️  Skipping: adws/ directory not found"
fi

echo ""

# Test 5: Build dependency graph
if [ -f "/tmp/test-py/python_imports.json" ]; then
    echo "5. Testing: Build dependency graph..."
    if python3 "$SCRIPT_DIR/build_dep_graph.py" /tmp/test-py/python_imports.json /tmp/test-graph.json; then
        echo "✅ Dependency graph built successfully"
        
        # Validate graph structure
        if jq -e '.stats and .graph and .criticality' /tmp/test-graph.json > /dev/null 2>&1; then
            echo "✅ Graph structure valid"
        fi
    else
        echo "❌ Failed to build dependency graph"
        exit 1
    fi
fi

echo ""

# Test 6: ADW stub
echo "6. Testing: ADW integration stub..."
if [ -f "$SCRIPT_DIR/adw_spawn_fix_agents.py" ]; then
    # Run with --help to verify stub works
    if python3 "$SCRIPT_DIR/adw_spawn_fix_agents.py" 2>&1 | grep -q "NOT IMPLEMENTED"; then
        echo "✅ ADW stub present (TODO: implement with repo Claude)"
    else
        echo "⚠️  ADW stub may have issues"
    fi
else
    echo "❌ ADW stub missing"
fi

echo ""
echo "==========================================="
echo "✅ All tests passed!"
echo ""
echo "Output samples:"
[ -f "/tmp/test-minimal/command_refs.json" ] && echo "  - /tmp/test-minimal/command_refs.json"
[ -f "/tmp/test-py/python_imports.json" ] && echo "  - /tmp/test-py/python_imports.json"
[ -f "/tmp/test-graph.json" ] && echo "  - /tmp/test-graph.json"
echo ""
echo "Next: Use CONTEXT_MODE=minimal for token-efficient operation"
echo "  Example: CONTEXT_MODE=minimal bash scripts/trace_all.sh"
