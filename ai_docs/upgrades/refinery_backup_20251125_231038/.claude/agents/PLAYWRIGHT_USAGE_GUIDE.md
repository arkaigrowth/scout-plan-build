# Playwright Usage Guide for Agents

## Quick Answer: Who Needs Playwright?

| Agent | Needs Playwright? | Why |
|-------|------------------|-----|
| **shadcn-frontend-architect** | ❌ No | Focuses on architecture & planning, not testing |
| **shadcn-ui-expert** | ❌ No | Provides implementation specs, not runtime testing |
| **frontend-debug** | ✅ Yes | Performs E2E testing, visual regression, browser debugging |

---

## Agent Responsibilities Breakdown

### 🏗️ shadcn-frontend-architect
**Role**: System design and architecture
**Output**: Plans, specifications, ADRs
**Testing**: Not responsible for testing
**Playwright**: **NOT NEEDED**

### 🎨 shadcn-ui-expert
**Role**: UI implementation details
**Output**: Component configurations, Tailwind classes
**Testing**: Not responsible for testing
**Playwright**: **NOT NEEDED**

### 🐛 frontend-debug
**Role**: Debug and fix runtime issues
**Output**: Fixed bugs, test results, error analysis
**Testing**: E2E tests, visual regression, interaction testing
**Playwright**: **NEEDED**

---

## Why This Separation Makes Sense

### Design Philosophy
```
Architecture (Planning) → Implementation (Building) → Testing (Validation)
     ↑                          ↑                          ↑
  Architect                 UI Expert               Frontend Debug
```

### Clear Boundaries
- **Architect**: "How should the system be structured?"
- **UI Expert**: "What components and props to use?"
- **Debugger**: "Is it actually working correctly?"

---

## When to Use Playwright

### Use Playwright for:
✅ **E2E Testing**: User flows, multi-page interactions
✅ **Visual Regression**: Screenshot comparisons
✅ **Browser Issues**: Cross-browser compatibility
✅ **Interaction Testing**: Click, type, scroll behaviors
✅ **Performance Testing**: Load times, rendering performance
✅ **Accessibility Testing**: Screen reader compatibility

### Don't Use Playwright for:
❌ **Architecture Planning**: Use documentation instead
❌ **Component Selection**: Use shadcn MCP instead
❌ **Static Analysis**: Use TypeScript, ESLint
❌ **Unit Testing**: Use Vitest or Jest
❌ **Style Checking**: Use design tokens, Tailwind

---

## Practical Examples

### Example 1: Building a Data Table

**Step 1: Architecture** (no Playwright)
```markdown
shadcn-frontend-architect:
- Designs table structure
- Plans data flow
- No testing needed
```

**Step 2: Implementation** (no Playwright)
```markdown
shadcn-ui-expert:
- Selects Table component
- Provides Tailwind classes
- No testing needed
```

**Step 3: Testing** (uses Playwright)
```markdown
frontend-debug:
- Tests table rendering with 10k rows
- Verifies filter functionality
- Checks responsive behavior
- Uses Playwright for E2E tests
```

### Example 2: Debugging Filter Issues

**User**: "The filters aren't working correctly"

**Wrong Approach**:
```markdown
shadcn-ui-expert tries to debug → ❌
(UI Expert doesn't do runtime testing)
```

**Right Approach**:
```markdown
frontend-debug agent:
1. Uses Playwright to reproduce issue
2. Tests filter interactions
3. Captures screenshots of broken state
4. Identifies and fixes the bug
```

---

## Setting Up Playwright (When Needed)

### For frontend-debug agent only:

```bash
# Install Playwright
npm install -D @playwright/test

# Install browsers
npx playwright install

# Create test file
mkdir -p tests/e2e
touch tests/e2e/data-table.spec.ts
```

### Example Playwright Test for Refinery
```typescript
// tests/e2e/filters.spec.ts
import { test, expect } from '@playwright/test';

test('text filter works correctly', async ({ page }) => {
  await page.goto('/');

  // Load CSV data
  await page.setInputFiles('input[type="file"]', 'test-data.csv');

  // Apply filter
  await page.fill('[data-testid="filter-input"]', 'product');
  await page.click('[data-testid="apply-filter"]');

  // Verify filtered results
  const rows = await page.locator('tbody tr').count();
  expect(rows).toBeLessThan(100); // Filtered from original
});
```

---

## Tool Configuration Updates

### Only frontend-debug needs Playwright tools:

```yaml
# frontend-debug.md
tools:
  - Read
  - Edit
  - Write
  - Bash
  - mcp__playwright__launch-browser  # If MCP available
  - mcp__playwright__screenshot
  - mcp__playwright__test-interaction
```

### Your shadcn agents DON'T need:
```yaml
# shadcn-frontend-architect.md
# shadcn-ui-expert.md
# NO Playwright tools needed
```

---

## Decision Tree: Which Agent to Use?

```
User Request
├─ "Design the component structure" → shadcn-frontend-architect
├─ "What props should the Table have?" → shadcn-ui-expert
├─ "The table isn't rendering correctly" → frontend-debug (with Playwright)
├─ "Test if filters work on mobile" → frontend-debug (with Playwright)
├─ "Plan the testing strategy" → shadcn-frontend-architect
└─ "Debug hydration errors" → frontend-debug (with Playwright)
```

---

## Recommendations

### For Your Refinery Project:

1. **Keep shadcn agents focused**: They work best doing architecture and implementation specs
2. **Use frontend-debug for runtime issues**: This is where Playwright shines
3. **Consider a test-automator agent**: If you need extensive test coverage

### Agent Invocation Pattern:
```javascript
// For planning/implementation (no Playwright)
Task({ subagent_type: "shadcn-frontend-architect" })
Task({ subagent_type: "shadcn-ui-expert" })

// For debugging/testing (uses Playwright)
Task({ subagent_type: "frontend-debug" })
```

---

## Summary

- ✅ **frontend-debug** is the ONLY agent that needs Playwright
- ❌ **shadcn agents** don't need Playwright (they plan and specify)
- 🎯 **Clear separation** = better agent performance
- 🔧 **Right tool for the job** = Playwright for testing, not planning

This separation keeps each agent focused and efficient at their specific role!

---

*Last Updated: 2024-11-17*