# Shadcn MCP Server Guide

## Overview

The shadcn MCP server provides direct access to shadcn/ui component documentation, examples, and installation commands within Claude Code.

---

## Setup Status

✅ **Configuration Created**: `.mcp.json` is properly configured
⚠️ **Activation Required**: Restart Claude Code to load the MCP server

### To Activate:
1. **Restart Claude Code** (close and reopen)
2. Look for confirmation that MCP servers loaded
3. New tools will appear prefixed with `mcp__shadcn-ui__`

---

## Available MCP Tools (after restart)

The shadcn MCP server typically provides these tools:

### 1. Component Lookup
```typescript
mcp__shadcn-ui__get-component(name: string)
// Returns: component documentation, props, examples
```

### 2. Component Installation
```typescript
mcp__shadcn-ui__install-component(name: string)
// Returns: installation command and dependencies
```

### 3. Theme Configuration
```typescript
mcp__shadcn-ui__get-theme()
// Returns: current theme configuration
```

### 4. Component Search
```typescript
mcp__shadcn-ui__search-components(query: string)
// Returns: matching components and descriptions
```

---

## Integration with Your Agents

### How Agents Use the MCP Server

Your agents can now access shadcn MCP tools directly:

#### shadcn-frontend-architect
```yaml
tools:
  - mcp__shadcn-ui__search-components  # Find components for architecture
  - mcp__shadcn-ui__get-component       # Verify component capabilities
```

#### shadcn-ui-expert
```yaml
tools:
  - mcp__shadcn-ui__get-component       # Get exact props and usage
  - mcp__shadcn-ui__install-component   # Get installation instructions
  - mcp__shadcn-ui__get-theme          # Check theme configuration
```

---

## Usage Examples

### Example 1: Getting Component Documentation

**Without MCP** (current):
```markdown
User: "How do I use the shadcn Dialog component?"
UI Expert: *Uses WebSearch or Context7 to find documentation*
```

**With MCP** (after restart):
```markdown
User: "How do I use the shadcn Dialog component?"
UI Expert: *Uses mcp__shadcn-ui__get-component("dialog")*
Returns: Exact props, examples, and accessibility guidelines
```

### Example 2: Installing Components

**Without MCP**:
```bash
# Manual lookup and installation
npx shadcn-ui@latest add dialog
```

**With MCP**:
```markdown
UI Expert uses: mcp__shadcn-ui__install-component("dialog")
Returns:
- Exact installation command
- Required dependencies
- File structure created
- Integration instructions
```

### Example 3: Architecture Planning

**Architect Agent with MCP**:
```markdown
Task: "Design a form system"

1. Use mcp__shadcn-ui__search-components("form")
   → Finds: Form, FormField, FormItem, FormLabel, FormControl, FormMessage

2. Use mcp__shadcn-ui__get-component("form")
   → Gets: react-hook-form integration, validation patterns

3. Creates architecture based on actual component capabilities
```

---

## Practical Workflows

### Workflow 1: Component Discovery
```
1. User: "I need a data display component"
2. Agent: mcp__shadcn-ui__search-components("data table list card")
3. MCP: Returns available components
4. Agent: Recommends best fit based on requirements
```

### Workflow 2: Implementation Details
```
1. User: "Implement a command palette"
2. UI Expert: mcp__shadcn-ui__get-component("command")
3. MCP: Returns props, keyboard navigation, search implementation
4. UI Expert: Provides exact implementation with proper props
```

### Workflow 3: Theme Consistency
```
1. User: "Make sure components match our theme"
2. Agent: mcp__shadcn-ui__get-theme()
3. MCP: Returns current theme tokens
4. Agent: Applies consistent styling
```

---

## Benefits Over Current Approach

### Current (WebSearch/Context7)
- May get outdated documentation
- Generic examples not specific to shadcn/ui
- No direct component installation info
- Requires interpretation and adaptation

### With shadcn MCP
- Always current shadcn/ui documentation
- Exact component API and props
- Direct installation commands
- Copy-paste ready examples
- Theme-aware recommendations

---

## Testing the MCP Server

After restarting Claude Code, test with:

```markdown
"Show me the exact props for the shadcn Button component"
```

Expected: Direct component documentation without web searches

```markdown
"How do I install the shadcn DataTable?"
```

Expected: Exact installation command and setup instructions

---

## Updating Agent Definitions

After MCP server is active, update your agents:

### Update shadcn-frontend-architect.md
```yaml
tools:
  - Read
  - Edit
  - Write
  - WebSearch
  - WebFetch
  - Grep
  - Glob
  - Task
  - mcp__shadcn-ui__search-components  # ADD
  - mcp__shadcn-ui__get-component       # ADD
  - mcp__context7__resolve-library-id
  - mcp__context7__get-library-docs
```

### Update shadcn-ui-expert.md
```yaml
tools:
  - Read
  - Edit
  - Write
  - WebSearch
  - WebFetch
  - Grep
  - Glob
  - Task
  - mcp__shadcn-ui__get-component       # ADD
  - mcp__shadcn-ui__install-component   # ADD
  - mcp__shadcn-ui__get-theme          # ADD
  - mcp__shadcn-ui__search-components  # ADD
```

---

## Troubleshooting

### MCP Server Not Available
1. Ensure `.mcp.json` is in project root
2. Restart Claude Code completely
3. Check for MCP server initialization messages
4. Try: "What MCP servers are available?"

### Tools Not Showing
- Tools appear as `mcp__shadcn-ui__[tool-name]`
- May need to reload the project
- Check if npx can access shadcn-ui-mcp-server

### Agent Can't Access MCP
- Update agent tool lists (see above)
- Ensure agent definitions include MCP tools
- Test with direct tool invocation first

---

## Advanced Usage

### Combining MCP with Agents

```javascript
// Architect creates structure
const architecture = await Task({
  subagent_type: "shadcn-frontend-architect",
  prompt: "Design dashboard with MCP component verification"
});

// UI Expert implements with MCP
const implementation = await Task({
  subagent_type: "shadcn-ui-expert",
  prompt: "Implement using MCP for exact shadcn/ui specs"
});
```

### Direct MCP Usage

You can also use MCP tools directly:
```markdown
"Use mcp__shadcn-ui__get-component to show me the Select component"
```

---

## Next Steps

1. **Restart Claude Code** to activate the MCP server
2. **Test** with simple component lookups
3. **Update agents** to include MCP tools (optional but recommended)
4. **Use** in your development workflow

The MCP server will make your shadcn/ui development much more efficient by providing direct access to component documentation and examples!

---

*Note: The exact tool names and capabilities depend on the shadcn-ui-mcp-server version. After restart, you can discover available tools by asking "What shadcn MCP tools are available?"*