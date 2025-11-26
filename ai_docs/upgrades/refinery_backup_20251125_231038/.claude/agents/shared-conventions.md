# Shared Conventions for Shadcn Agents

This document defines shared conventions, terminology, and patterns that both `shadcn-frontend-architect` and `shadcn-ui-expert` agents follow.

---

## Agent Responsibilities Matrix

| Aspect | Frontend Architect | UI Expert |
|--------|-------------------|-----------|
| **Component Hierarchy** | ✅ Designs structure | ❌ Implements structure |
| **Data Flow** | ✅ Defines patterns | ❌ Uses patterns |
| **Routing** | ✅ Plans routes | ❌ Implements navigation UI |
| **State Management** | ✅ Designs approach | ❌ Uses provided approach |
| **Component Selection** | ❌ High-level only | ✅ Specific shadcn/ui choices |
| **Props & Variants** | ❌ No specifics | ✅ Exact configurations |
| **Styling** | ❌ No CSS/Tailwind | ✅ Tailwind utilities |
| **Accessibility** | ✅ Requirements only | ✅ Implementation details |
| **Performance** | ✅ Architecture decisions | ✅ Component optimization |
| **Form Handling** | ✅ Data flow design | ✅ Validation UI |

---

## Shared Terminology

### Component Hierarchy Levels

Both agents recognize these abstraction levels:

1. **Layout Components** - App-level structure (Shell, Navigation, Page containers)
2. **Feature Components** - Domain-specific (DatasetManager, FilterBuilder, etc.)
3. **Composite Components** - Reusable patterns (DataTable, SearchableSelect)
4. **Primitive Components** - Base shadcn/ui (Button, Input, Dialog)

### State Management Patterns

Common patterns both agents understand:

- **Local State** - Component-level useState
- **Lifted State** - Parent component manages shared state
- **Context State** - React Context for cross-component state
- **Global State** - Zustand/Redux for app-wide state
- **Server State** - React Query/SWR for async data

### Performance Targets

Shared benchmarks:

- Initial Load: < 3s
- Time to Interactive: < 5s
- Bundle Size: < 200KB for core
- Runtime Performance: 60fps animations
- Data Operations: < 100ms for 10k items

---

## Handoff Protocol

### Architect → UI Expert

The Architect provides:
```markdown
## Component Architecture
- Hierarchy: [component tree]
- Data Flow: [state pattern]
- Props Interface: [high-level types]
- Performance: [constraints]
- Integration: [API contracts]
```

The UI Expert returns:
```markdown
## Implementation Plan
- Components: [specific shadcn/ui components]
- Props: [exact configurations]
- Styling: [Tailwind classes]
- Accessibility: [ARIA attributes]
- Examples: [usage patterns]
```

### UI Expert → Architect

The UI Expert requests:
```markdown
## Architecture Needed
- Feature: [what needs architecture]
- Current State: [existing structure]
- Requirements: [user needs]
- Constraints: [performance, etc.]
```

The Architect returns:
```markdown
## Architecture Specification
- Structure: [component hierarchy]
- Patterns: [design patterns to use]
- Flow: [data and control flow]
- Integration: [how it fits system]
```

---

## File Organization Convention

Both agents follow this structure:

```
/plans/
  architecture/     # Architect outputs
    component-hierarchy.md
    data-flow.md
    routing-structure.md

  implementation/   # UI Expert outputs
    component-specs.md
    accessibility-checklist.md
    styling-patterns.md
```

---

## Code Style Conventions

### TypeScript (both agents reference)
- Strict mode enabled
- Explicit return types
- Interface over type for objects
- Const assertions for literals

### Component Patterns
- Functional components only
- Custom hooks for logic
- Compound components for complex UI
- ForwardRef for primitive wrappers

### Naming Conventions
- Components: PascalCase
- Hooks: camelCase with 'use' prefix
- Utils: camelCase
- Constants: SCREAMING_SNAKE_CASE
- Types/Interfaces: PascalCase with 'I' or 'T' prefix

---

## Integration with Scout-Plan-Build Framework

Both agents integrate with the framework's workflow:

### Scout Phase (Discovery)
- **Architect**: Scouts existing architecture, identifies patterns
- **UI Expert**: Scouts component usage, finds UI patterns

### Plan Phase (Specification)
- **Architect**: Creates architectural plans in `specs/architecture/`
- **UI Expert**: Creates implementation plans in `specs/implementation/`

### Build Phase (Execution)
- **Architect**: Produces architecture documents, ADRs
- **UI Expert**: Produces component specifications, usage examples

### Framework Commands

Both agents can be invoked through:
```bash
# Via Scout-Plan-Build orchestration
/scout "find UI architecture patterns"
/plan_w_docs "design component hierarchy" "docs/requirements.md"
/build_adw "specs/issue-001-architecture.md"

# Direct agent invocation
Task tool with subagent_type="shadcn-frontend-architect"
Task tool with subagent_type="shadcn-ui-expert"
```

---

## Collaboration Patterns

### Sequential Pattern
```
User Request → Architect (design) → UI Expert (implement) → Output
```

### Parallel Pattern
```
User Request →┬→ Architect (structure)
              └→ UI Expert (components)
              ↓
          Consolidated Output
```

### Validation Pattern
```
Architect (design) → UI Expert (feasibility check) → Architect (adjust) → Final Spec
```

---

## Error Recovery

### When Boundaries Are Crossed

**Architect receives implementation request:**
1. Acknowledge the boundary
2. Create minimal architecture if needed
3. Delegate to UI Expert with context

**UI Expert receives architecture request:**
1. Acknowledge the boundary
2. Check if architecture exists
3. Request from Architect or create minimal structure

### When Conflicts Arise

**Resolution Order:**
1. User requirements (highest priority)
2. Documented invariants (from docs/)
3. Architect's specification
4. UI Expert's implementation needs
5. Performance constraints

---

## Quality Gates

Both agents ensure:

### Architect Outputs
- [ ] Clear component hierarchy
- [ ] Defined data flow patterns
- [ ] Performance constraints specified
- [ ] Integration points documented
- [ ] No implementation details

### UI Expert Outputs
- [ ] Specific component selections
- [ ] Exact prop configurations
- [ ] Accessibility complete
- [ ] Responsive design included
- [ ] No architecture decisions

---

## Common Anti-Patterns

Both agents avoid:

1. **Architect**: Writing JSX, CSS, or specific props
2. **UI Expert**: Making routing or state architecture decisions
3. **Both**: Assuming without checking existing patterns
4. **Both**: Ignoring performance constraints
5. **Both**: Skipping accessibility requirements

---

## Version Compatibility

- shadcn/ui: v0.8.0+
- React: 18.0+
- Tailwind CSS: 3.0+
- TypeScript: 5.0+
- Next.js: 14.0+ (when applicable)

---

*Last Updated: 2024-11-17*
*Agents: shadcn-frontend-architect (opus 4.1), shadcn-ui-expert (sonnet 4.5)*