#!/bin/bash
# Fix agent frontmatter - add missing "name" field
# Fixes Claude Code parser errors

set -e

echo "🔧 Fixing Agent Frontmatter"
echo "============================"
echo ""

AGENT_DIR="$HOME/.claude/agents"

# Check if agents directory exists
if [ ! -d "$AGENT_DIR" ]; then
    echo "❌ No agents directory found at $AGENT_DIR"
    exit 1
fi

# Fix interview-coach.md
echo "📝 Fixing interview-coach.md..."
if [ -f "$AGENT_DIR/interview-coach.md" ]; then
    # Create temp file with frontmatter
    cat > "$AGENT_DIR/interview-coach.md.tmp" << 'EOF'
---
name: interview-coach
description: Technical interview preparation and behavioral coaching specialist
---

EOF

    # Append original content (skip if it already has frontmatter)
    if grep -q "^---$" "$AGENT_DIR/interview-coach.md"; then
        # Already has frontmatter, skip
        rm "$AGENT_DIR/interview-coach.md.tmp"
        echo "   ⚠️  Already has frontmatter, skipping"
    else
        cat "$AGENT_DIR/interview-coach.md" >> "$AGENT_DIR/interview-coach.md.tmp"
        mv "$AGENT_DIR/interview-coach.md.tmp" "$AGENT_DIR/interview-coach.md"
        echo "   ✅ Fixed"
    fi
fi

# Fix vsl-director.md
echo "📝 Fixing vsl-director.md..."
if [ -f "$AGENT_DIR/vsl-director.md" ]; then
    cat > "$AGENT_DIR/vsl-director.md.tmp" << 'EOF'
---
name: vsl-director
description: Video sales letter creation and marketing content specialist
---

EOF

    if grep -q "^---$" "$AGENT_DIR/vsl-director.md"; then
        rm "$AGENT_DIR/vsl-director.md.tmp"
        echo "   ⚠️  Already has frontmatter, skipping"
    else
        cat "$AGENT_DIR/vsl-director.md" >> "$AGENT_DIR/vsl-director.md.tmp"
        mv "$AGENT_DIR/vsl-director.md.tmp" "$AGENT_DIR/vsl-director.md"
        echo "   ✅ Fixed"
    fi
fi

# Fix outreach-orchestrator.md
echo "📝 Fixing outreach-orchestrator.md..."
if [ -f "$AGENT_DIR/outreach-orchestrator.md" ]; then
    cat > "$AGENT_DIR/outreach-orchestrator.md.tmp" << 'EOF'
---
name: outreach-orchestrator
description: Automated outreach campaign management and email/LinkedIn automation
---

EOF

    if grep -q "^---$" "$AGENT_DIR/outreach-orchestrator.md"; then
        rm "$AGENT_DIR/outreach-orchestrator.md.tmp"
        echo "   ⚠️  Already has frontmatter, skipping"
    else
        cat "$AGENT_DIR/outreach-orchestrator.md" >> "$AGENT_DIR/outreach-orchestrator.md.tmp"
        mv "$AGENT_DIR/outreach-orchestrator.md.tmp" "$AGENT_DIR/outreach-orchestrator.md"
        echo "   ✅ Fixed"
    fi
fi

echo ""
echo "✨ Frontmatter Fix Complete!"
echo "==========================="
echo ""
echo "Run 'claude doctor' to verify parser errors are gone."
echo ""
echo "All agents should now have proper frontmatter format:"
echo "---"
echo "name: agent-name"
echo "description: Agent description"
echo "---"