# Coach Mode - Transparent AI Workflow Guidance

**Learn how AI thinks while it works.**

Coach Mode makes Claude's decision-making visible, showing you the journey through complex tasks with progress indicators, decision explanations, and educational insights.

---

## Quick Start

```bash
/coach              # Toggle on/off
/coach minimal      # Symbols only (~5% overhead)
/coach full         # Maximum detail (~30% overhead)
/output-style coach # Direct activation (balanced ~15%)
```

---

## Three Levels

| Level | Command | Overhead | Best For |
|-------|---------|----------|----------|
| **Minimal** | `/coach minimal` | ~5% | Experienced users, long operations |
| **Balanced** | `/coach` | ~15% | Daily use, learning workflows |
| **Full** | `/coach full` | ~30% | Understanding complex decisions |

---

## What You'll See

### Journey Boxes (task start)
```
┌─────────────────────────────────────────────────┐
│ 📍 Journey: Implement OAuth2                    │
│ ─────────────────────────────────────────────── │
│ [▶ Scout] → [Plan] → [Build] → [Test]          │
│                                                 │
│ 🎯 Goal: Add OAuth2 login flow                 │
│ 📊 Estimated: 4 steps                          │
└─────────────────────────────────────────────────┘
```

### Decision Points
```
🤔 Decision: Which auth library?

| Option | Trade-off |
|--------|-----------|
| A) passport.js | Popular, more setup |
| B) next-auth | Simpler, Next.js only |

→ Choosing: B (matches your stack)
```

### Tool Insights
```
⚙️ Using: Grep → searching for existing auth patterns
   └─ Found: 3 files with authentication logic
```

### Progress Updates
```
📊 Progress: 2/4 complete
   └─ Done: Scout, Plan
   └─ Next: Build implementation
```

---

## Symbol Vocabulary

| Symbol | Meaning | Usage |
|--------|---------|-------|
| 📍 | Position | Current stage in journey |
| 🎯 | Goal | What we're achieving |
| 🤔 | Decision | Choice point with options |
| 💡 | Insight | Educational moment |
| ⚙️ | Tool | About to use a tool |
| 📊 | Progress | Step X of Y |
| ✅ | Complete | Task finished |
| ❌ | Failed | Error occurred |
| ⚠️ | Warning | Attention needed |
| → » | Flow | Leads to, sequence |

---

## Minimal Mode Example

When overhead matters, minimal mode uses inline symbols:

```
📍 1/4 Scout → ⚙️ Grep auth... ✅ (5 files)
📍 2/4 Plan → 🤔 spec structure... ✅ saved
📍 3/4 Build → ⚙️ Edit 3 files... ✅
📍 4/4 Test → ⚙️ pytest... ✅ all pass
```

---

## Configuration

Coach mode styles are stored in:
- User-level: `~/.claude/output-styles/coach*.md`
- Project-level: `.claude/commands/coach.md` (toggle command)

To customize, copy and modify the output style files.

---

## When to Use Each Level

| Situation | Recommended |
|-----------|-------------|
| Learning the framework | `full` |
| Daily development | `balanced` (default) |
| Long batch operations | `minimal` |
| Demos/presentations | `full` |
| Tight context budget | `minimal` or off |

---

## Related

- [Output Styles](https://docs.anthropic.com/claude-code/output-styles) - Claude Code documentation
- [Slash Commands](../CLAUDE.md) - Framework command reference
