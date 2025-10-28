# Architecture Diagrams

This directory contains individual architecture diagrams that are combined into the comprehensive [SHAREABLE_ARCHITECTURE.md](../SHAREABLE_ARCHITECTURE.md).

## Main Document

**📄 [SHAREABLE_ARCHITECTURE.md](../SHAREABLE_ARCHITECTURE.md)** - Complete architecture reference
- GitHub-ready with properly formatted Mermaid diagrams
- Includes all diagrams from this directory
- Complete performance metrics and lessons learned
- Quick start guide and future roadmap
- Perfect for sharing, presentations, or PDF conversion

## Individual Diagrams

These files contain detailed diagrams for specific aspects of the system:

### 1. [system-architecture-overview.md](./system-architecture-overview.md)
- Three-layer architecture overview
- Complete workflow data flow
- Layer-by-layer analysis
- Performance implications
- Integration points

**Key Diagrams**:
- Three-layer architecture (UI → Orchestration → Infrastructure)
- Complete workflow data flow
- State management flow
- Parallel vs sequential execution timelines

### 2. [parallel-execution-sequence.md](./parallel-execution-sequence.md)
- Parallel execution sequence diagram
- Performance metrics (40-50% speedup)
- Git conflict resolution strategy
- Simple 30-line implementation

**Key Diagrams**:
- Parallel execution sequence with subprocess.Popen()
- Git conflict problem and solution
- Time comparison: sequential vs parallel
- Implementation complexity analysis

### 3. [component-interaction-uml.md](./component-interaction-uml.md)
- ADW module architecture
- Component relationships
- Security and validation architecture
- Data flow patterns

**Key Diagrams**:
- UML class diagram of all ADW modules
- Module-by-module breakdown
- Security validation chain
- State management lifecycle

### 4. [scout-plan-build-pipeline.md](./scout-plan-build-pipeline.md)
- Complete pipeline workflow
- Phase-by-phase breakdown
- Reality vs documentation
- Error handling

**Key Diagrams**:
- Complete pipeline flowchart with color-coded status
- Phase breakdown (Scout → Plan → Build → Parallel → Finalize)
- Working vs non-working tool patterns
- Performance optimization timeline

## Viewing Diagrams

### On GitHub
All Mermaid diagrams render automatically on GitHub. Just open any file and scroll.

### Locally
Use one of these tools:
- **VSCode**: Install "Markdown Preview Mermaid Support" extension
- **IntelliJ/WebStorm**: Built-in Mermaid support
- **Online**: Copy diagram code to https://mermaid.live/

### PDF Export
Use the main [SHAREABLE_ARCHITECTURE.md](../SHAREABLE_ARCHITECTURE.md) for PDF conversion:
- **Chrome/Edge**: Print → Save as PDF
- **Pandoc**: `pandoc SHAREABLE_ARCHITECTURE.md -o architecture.pdf`
- **Markdown to PDF extension**: Various VSCode/browser extensions

## Diagram Types Used

- **Flowchart**: Pipeline workflows, decision trees
- **Sequence Diagram**: Parallel execution, API interactions
- **Class Diagram**: Component relationships (UML)
- **Gantt Chart**: Performance timelines
- **State Diagram**: State management lifecycle
- **Mind Map**: System boundaries and constraints
- **Graph**: Network relationships

## Color Scheme

Consistent color coding across all diagrams:

| Color | Meaning | Usage |
|-------|---------|-------|
| 🟢 Green (#90EE90) | Working, Production | Successfully implemented features |
| 🔵 Blue (#E1F5FE) | Parallel | Parallel execution components |
| 🟡 Yellow (#FFE4B5) | Partial | Partially working features |
| 🔴 Red (#FFB6C1) | Broken | Non-functional features |
| 🟤 Brown (#E8F5E9) | Git Operations | Git commands |
| 🟣 Purple (#FFF9C4) | Decision Points | Conditional logic |

## Key Metrics Visualized

All diagrams include these key metrics:

- **40-50% Performance Improvement**: Parallel execution speedup
- **30 Lines vs 150+ Lines**: Simplicity comparison
- **8-11 min vs 12-17 min**: Time savings
- **100% Security**: Zero injection vulnerabilities with Pydantic
- **80%+ Working Rate**: Most phases functional in production

## Updates and Maintenance

These diagrams reflect the system state as of **2025-01-27**.

When updating:
1. Update individual diagram files in this directory
2. Regenerate the main [SHAREABLE_ARCHITECTURE.md](../SHAREABLE_ARCHITECTURE.md)
3. Update version metadata at the bottom
4. Test all Mermaid diagrams render on GitHub

## Related Documentation

- [../../CLAUDE.md](../../../CLAUDE.md) - Implementation guide
- [../PORTABILITY_ANALYSIS.md](../PORTABILITY_ANALYSIS.md) - Deployment guide
- [../../../specs/](../../../specs/) - Implementation specs
- [../../../docs/](../../../docs/) - User documentation

---

**Tip**: Start with [SHAREABLE_ARCHITECTURE.md](../SHAREABLE_ARCHITECTURE.md) for the complete picture, then dive into individual files for deep dives on specific topics.
