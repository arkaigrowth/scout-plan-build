# Refinery Data Refiner - Claude Code Instructions

**Project Type:** TypeScript data-cleaning engine for e-commerce (Shopify-first)
**Framework:** Scout-Plan-Build v2024.11.8 installed
**Your Role:** Help implement stubbed modules following documented invariants

---

## 📋 Project Context

This repo is a **data-cleaning engine + workspace scaffold** with:

- **Core Engine** (`src/lib/dataset/`): Patch engine, filters, selectors (stubbed → implement)
- **CSV Parser** (`src/lib/csv/`): Column inference, type coercion (stubbed → implement)
- **State Management** (`src/lib/state/`): Zustand store (stubbed → implement)
- **Documentation** (`docs/`): INVARIANTS.md, AGENT_PROTOCOL.md, SCAFFOLDS.md, PERF_NOTES.md

**Intentionally stubbed implementations** - your job is to fill them in while respecting documented constraints.

---

## 🎯 Source of Truth: docs/

**CRITICAL:** Always reference these documents when implementing:

1. **docs/INVARIANTS.md** - Hard constraints (immutability, performance targets)
2. **docs/AGENT_PROTOCOL.md** - How agents should interact with engine
3. **docs/SCAFFOLDS.md** - Code patterns and examples to follow
4. **docs/PERF_NOTES.md** - Performance expectations (<50ms for 10k rows, etc.)

When asked to implement something, **always read the relevant docs first** to understand constraints.

---

## ⚙️ Framework Integration

The Scout-Plan-Build framework is installed in this repo:
- `adws/` - Framework Python modules
- `specs/` - Implementation plans (generated)
- `ai_docs/` - Build reports and reviews (generated)
- `.adw_config.json` - TypeScript project configuration

**You don't need to set up anything** - the framework is ready to use with natural language.

---

## 💡 How to Use the Framework

### **Natural Language (Recommended)**

Just describe what to implement, referencing the docs:

```
"Implement the patch engine in src/lib/dataset/dataset-engine.ts.

Follow docs/INVARIANTS.md section 'Patch Engine Rules':
- Immutable patches: {rowId, columnKey, newValue, timestamp}
- Apply to originalRows → compiledRows (no mutations)
- Audit history for undo/redo
- Target: <50ms for 10k rows + 100 patches

Use TypeScript strict mode + Vitest tests."
```

The framework will:
1. Scout relevant files and docs
2. Create implementation plan in `specs/`
3. Build the feature respecting documented constraints
4. Generate Vitest tests
5. Create build report in `ai_docs/build_reports/`

### **Explicit Commands (Advanced)**

For precise control:
- `/scout "description" "4"` - Find relevant files
- `/plan_w_docs "task" "docs/INVARIANTS.md" "scout_outputs/relevant_files.json"` - Create plan
- `/build_adw "specs/issue-001-*.md"` - Build from plan

---

## 🏗️ Implementation Priorities

### Phase 1: Core Engine
1. Patch engine (`src/lib/dataset/dataset-engine.ts`)
2. CSV parser with type inference (`src/lib/csv/csv-parser.ts`)
3. Dataset selectors (`src/lib/dataset/dataset-selectors.ts`)
4. Zustand store completion (`src/lib/state/dataset-store.ts`)

### Phase 2: Filters
1. Text filters (contains, equals, startsWith, endsWith, regex)
2. Number filters (<, >, =, between)
3. Date filters (before, after, between)
4. Filter composition (AND/OR logic)

### Phase 3: Advanced Features
1. Group-by functionality
2. Agent run tracking
3. CSV export with filters
4. Undo/redo system

---

## ✅ Code Requirements

All implementations must:
- ✅ Use **TypeScript strict mode** with explicit return types
- ✅ Follow patterns from `src/lib/dataset/types.ts`
- ✅ Never mutate `originalRows` (immutability invariant)
- ✅ Include **Vitest tests** (unit + performance benchmarks)
- ✅ Meet performance targets from `docs/PERF_NOTES.md`
- ✅ Use **structural sharing** for efficiency (don't clone entire datasets)
- ✅ Add JSDoc comments for public APIs

---

## 📚 Key References

| File | Purpose |
|------|---------|
| **docs/INVARIANTS.md** | Hard constraints - READ FIRST |
| **docs/SCAFFOLDS.md** | Code patterns to follow |
| **docs/PERF_NOTES.md** | Performance benchmarks |
| **FRAMEWORK_USAGE.md** | Comprehensive framework guide (548 lines) |
| **src/lib/dataset/types.ts** | Existing type definitions |
| **.adw_config.json** | Framework configuration |

---

## 🎯 Example Tasks (Copy-Paste Ready)

### Implement Patch Engine
```
Implement the patch engine in src/lib/dataset/dataset-engine.ts.

From docs/INVARIANTS.md section "Patch Engine Rules":
- Patches: {rowId, columnKey, newValue, timestamp, userId?}
- Function: applyPatches(originalRows, patches) → compiledRows
- Never mutate originalRows (create new array with structural sharing)
- Maintain audit history: getPatchHistory() returns all patches chronologically
- Support revertPatch(patchId) for undo
- Performance: <50ms for 10k rows + 100 patches

Use TypeScript strict mode. Add Vitest tests for:
- Immutability (original rows never change)
- Audit history (all patches tracked)
- Performance (benchmark with 10k rows)
- Edge cases (invalid rowId, missing columns)

Follow patterns from src/lib/dataset/types.ts.
```

### Implement CSV Parser
```
Implement CSV parser in src/lib/csv/csv-parser.ts.

From docs/INVARIANTS.md section "CSV Parsing":
- Column type inference: try number → date → boolean → string
- Number: parseInt/parseFloat (check !isNaN)
- Date: ISO 8601 regex pattern
- Boolean: true/false, yes/no, 1/0 (case insensitive)
- Coercion modes:
  - strict: throw on coercion errors
  - lenient: coerce errors → null
  - skip-errors: skip rows with errors

Export: parseCSV(csv: string, options: ParseOptions) → ParseResult
Add Vitest tests for all type inference cases.
```

### Implement Text Filters
```
Implement text filters in src/lib/dataset/filters.ts.

From docs/SCAFFOLDS.md, support:
- TextFilter type: {type: 'text', column: string, operator: 'contains'|'equals'|'startsWith'|'endsWith'|'regex', value: string}
- Function: applyTextFilter(rows, filter) → filteredRows
- Operators: case-insensitive by default (add caseSensitive?: boolean option)
- Regex: compile once, cache for performance

Performance: <100ms for 50k rows with 5 filters
Add Vitest tests for each operator + composition.
```

---

## 🐛 Common Patterns

### Reading Docs Before Implementation
```
# Step 1: Check what docs say
"What does docs/INVARIANTS.md say about patch engine immutability?"

# Step 2: Implement based on constraints
"Implement patch engine following the immutability rules you just read"
```

### Performance Validation
```
# After implementation
"Benchmark the patch engine with 10k rows + 100 patches.
Verify it meets the <50ms target from docs/PERF_NOTES.md."
```

### Test-Driven Approach
```
"First write Vitest tests for the patch engine based on docs/INVARIANTS.md examples.
Then implement the engine to pass those tests."
```

---

## 🚨 Important Notes

1. **Always read docs first** - Don't guess at constraints
2. **Never mutate originalRows** - This is a hard invariant
3. **Use structural sharing** - Don't clone entire datasets for performance
4. **Add performance tests** - Verify benchmarks from PERF_NOTES.md
5. **Reference existing types** - Use types.ts as the foundation

---

## 📖 Need More Help?

- **Comprehensive guide**: See `FRAMEWORK_USAGE.md` (548 lines with detailed examples)
- **Test installation**: Run `python test_installation.py`
- **Validate setup**: Run `./scripts/validate_pipeline.sh`

---

**Ready to build!** 🚀
