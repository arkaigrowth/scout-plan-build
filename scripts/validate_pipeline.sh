#!/bin/bash
# Pipeline Validation - Proves everything works
# Run this at the start of each session

echo "🧪 PIPELINE VALIDATION TEST"
echo "=========================="

# Test 1: Scout works
echo -n "1. Testing Scout... "
python adws/scout_simple.py "test" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Works"
else
    echo "❌ Failed"
fi

# Test 2: Scout output exists
echo -n "2. Scout creates output... "
if [ -f "scout_outputs/relevant_files.json" ]; then
    echo "✅ Yes"
else
    echo "❌ No"
fi

# Test 3: Plan command exists
echo -n "3. Plan command exists... "
if [ -f ".claude/commands/planning/plan_w_docs_improved.md" ]; then
    echo "✅ Yes"
else
    echo "❌ No"
fi

# Test 4: Build command exists
echo -n "4. Build command exists... "
if [ -f ".claude/commands/workflow/build.md" ]; then
    echo "✅ Yes"
else
    echo "❌ No"
fi

echo ""
echo "Ready to use:"
echo "  /scout 'your task' '3'"
echo "  /plan_w_docs_improved 'task' '' 'scout_outputs/relevant_files.json'"
echo "  /build 'specs/your-spec.md'"