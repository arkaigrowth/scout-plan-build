# Shadcn MCP Quick Reference

## 🚀 Quick Start

1. **You've already done**: Created `.mcp.json` ✅
2. **Next step**: **RESTART Claude Code** to activate
3. **Verify**: Ask "What shadcn MCP tools are available?"

---

## 🛠️ Available Tools (after restart)

| Tool | Purpose | Example Usage |
|------|---------|---------------|
| `mcp__shadcn-ui__get-component` | Get component docs & props | `"Show Button component from MCP"` |
| `mcp__shadcn-ui__search-components` | Find components | `"Search for form components"` |
| `mcp__shadcn-ui__install-component` | Get install command | `"How to install Dialog?"` |
| `mcp__shadcn-ui__get-theme` | Check theme config | `"Show current theme"` |

---

## 📝 Common Commands

### Direct Usage
```markdown
"Use mcp__shadcn-ui__get-component to show the Table component"
"Search shadcn MCP for data display components"
"Get installation instructions for Select from MCP"
```

### With Your Agents
```markdown
"Have shadcn-ui-expert use MCP to implement a data table"
"Ask shadcn-frontend-architect to verify component availability via MCP"
```

### For Your Refinery Project
```markdown
"Use MCP to implement the filter panel from docs/INVARIANTS.md"
"Get shadcn patterns for the CSV parser UI"
"Show MCP examples for the patch editor dialog"
```

---

## ✅ Verification Commands

After restart, test with these:

```bash
# Test 1: Check if MCP loaded
"What MCP servers are currently active?"

# Test 2: Try component lookup
"Get the Button component from shadcn MCP"

# Test 3: Search functionality
"Search shadcn MCP for 'table'"

# Test 4: With agents
"Have shadcn-ui-expert use MCP to show Dialog usage"
```

---

## 🔄 If MCP Not Working

1. **Check restart**: Did you fully close and reopen Claude Code?
2. **Check config**: Is `.mcp.json` in project root?
3. **Check npm**: Can you run `npx shadcn-ui-mcp-server` manually?
4. **Check tools**: Do you see tools starting with `mcp__shadcn-ui__`?

---

## 📍 Your Current Status

- ✅ `.mcp.json` configured correctly
- ⏳ Awaiting Claude Code restart
- 🎯 Ready to use once restarted

**Next Action**: Restart Claude Code now!

---

*After restart, this MCP will make your shadcn/ui development much faster!*