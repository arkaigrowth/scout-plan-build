# Hooks & Skills Analysis - Installation Gaps

## 🔴 Critical Oversights Found

You caught **THREE major gaps** in our installation system:

### 1. ❌ Hooks Not Being Installed
**Problem**: `.claude/hooks/` folder (8 files + utils) not copied to new repos

**What We're Missing**:
```
.claude/hooks/
├── notification.py         # Notification events
├── post_tool_use.py        # After tool execution
├── pre_compact.py          # Before compacting context
├── pre_tool_use.py         # Before tool execution (5KB - complex)
├── stop.py                 # Session stop events
├── subagent_stop.py        # Subagent completion
├── user_prompt_submit.py   # Prompt validation & logging
└── utils/
    ├── constants.py        # Shared utilities
    └── llm/               # LLM utilities
```

**Why This Matters**:
- **Logging**: Hooks create session logs in `logs/[session-id]/`
- **Validation**: Pre-hooks validate inputs for security
- **Debugging**: Post-hooks help trace execution
- **Observability**: Complete audit trail of all operations

**Should They Be Portable?**
- ✅ **YES** - These are foundational to the workflow
- ✅ Generic logging/validation works for any repo
- ⚠️ But some repos might not want all hooks (configurable?)

---

### 2. ❌ Skills Not Being Installed
**Problem**: `.claude/skills/` folder (3 files) not copied to new repos

**What We're Missing**:
```
.claude/skills/
├── adw-scout.md       # 10KB - Intelligent scout with memory
├── adw-complete.md    # 16KB - Complete workflow orchestrator
└── README.md          # 4KB - Skills documentation
```

**Why This Matters**:
- **Skills are fundamental** - You said it yourself!
- `adw-scout` - Enhanced scout with memory and robustness (85/100)
- `adw-complete` - Full workflow orchestration with transaction support (90/100)
- These provide higher-level abstractions over slash commands

**From skills/README.md**:
- High determinism (sorted outputs, fixed seeds)
- Robustness patterns (VALID pattern, fallbacks)
- Memory integration (learns from each run)

**Should They Be Portable?**
- ✅ **ABSOLUTELY YES** - Core building blocks
- These ARE the workflow in skill form
- Tax-prep repo would benefit from same skills

---

### 3. ⚠️ `.claude/agents/` Folder Confusion
**Your Question**: "where did this repo's .claude/agents folder go? why don't we have one? shouldn't we??"

**Answer**: We intentionally deleted it because it was **empty**!

**The Architecture**:
```
~/.claude/agents/          # User's GLOBAL agent definitions
├── duckdb-data-analyst.md # Personal custom agents
├── interview-coach.md     # Work across ALL projects
└── AGENTS_INDEX.md        # We just cleaned this!

project/.claude/agents/    # ❌ NOT NEEDED
                          # Agents are global, not per-project

project/.claude/commands/  # ✅ SLASH COMMANDS (project-specific)
project/.claude/skills/    # ✅ SKILLS (project-specific)
```

**Why No Repo-Level Agents?**
- Agent definitions are **persona/expertise** based
- They're **tool choices**, not workflow steps
- Same agent (python-expert) works for ANY Python project
- No need to duplicate them per-repo

**Analogy**:
- Skills = "How to do X in THIS project"
- Commands = "Project-specific workflows"
- Agents = "I know how to do Y" (universal expertise)

**Should We Add It Back?**
- ❌ **NO** - Architecture is correct
- Agents belong in user home (`~/.claude/agents/`)
- Projects have commands and skills instead

---

## 🔧 What Should Be Installed?

| Component | Location | Should Install? | Why |
|-----------|----------|-----------------|-----|
| **Hooks** | `.claude/hooks/` | ✅ YES | Logging, validation, observability |
| **Skills** | `.claude/skills/` | ✅ YES | Core workflow building blocks |
| **Commands** | `.claude/commands/` | ✅ ALREADY DOING | Project workflows |
| **Agents** | `.claude/agents/` | ❌ NO | Global user config, not repo |
| **State** | `.claude/state/` | ⚠️ CREATE EMPTY | For workflow persistence |
| **Memory** | `.claude/memory/` | ⚠️ CREATE EMPTY | For skill memory |

---

## 📊 Impact of Current Gaps

### Without Hooks
```bash
# User in tax-prep repo runs workflow
/scout "find tax forms"

# What happens:
✅ Scout runs
❌ No logging of what it did
❌ No validation of inputs
❌ No session audit trail
❌ Can't debug failures later
```

### Without Skills
```bash
# User in tax-prep repo wants orchestrated workflow
# What they have to do:
/scout "task"           # Manual step 1
/plan_w_docs "..."      # Manual step 2
/build_adw "..."        # Manual step 3

# What they COULD do with skills:
/adw-complete "task"    # ONE command, fully orchestrated!
```

**Skills provide**:
- Memory across runs
- Error recovery
- Transaction support
- Robustness patterns

---

## 🎯 Recommendations

### 1. Update Installer to Include Hooks
```bash
# Add to scripts/install_to_new_repo.sh
cp -r "$SOURCE_DIR/.claude/hooks" "$TARGET_REPO/.claude/"
```

**Considerations**:
- Copy all hooks + utils
- Check if uv dependencies are satisfied
- Maybe make hooks optional with flag?

### 2. Update Installer to Include Skills
```bash
# Add to scripts/install_to_new_repo.sh
cp -r "$SOURCE_DIR/.claude/skills" "$TARGET_REPO/.claude/"
```

**Considerations**:
- Skills are fundamental, should always install
- Update CLAUDE.md in target to document skills

### 3. Document Agent Architecture
Create `.claude/ARCHITECTURE.md` explaining:
- Why agents are global (home directory)
- Why skills/commands are local (repo directory)
- How they interact

### 4. Create Empty State/Memory Directories
```bash
mkdir -p "$TARGET_REPO/.claude/state"
mkdir -p "$TARGET_REPO/.claude/memory"
```

---

## ⚠️ Potential Issues

### Hook Dependencies
Hooks use `uv run --script` and require:
- Python 3.11+
- python-dotenv
- Custom utils (we'd copy those)

**Solution**: Check in installer, warn if missing

### Skills Complexity
Skills are sophisticated (16KB files with memory/transaction logic)

**Solution**: Include but document well

### Repository Size
Adding hooks + skills + utils ≈ 50KB of Python code

**Solution**: Worth it for the functionality

---

## 📚 Documentation Gaps

Currently missing from docs:
1. Hooks system explanation
2. Skills vs Commands vs Agents
3. When to use what
4. How memory/state work

**Need to add**:
- Hooks guide
- Skills guide
- Architecture diagram
- Decision tree for tool selection

---

## ✅ Action Plan

1. **Immediate**: Update installer to copy hooks + skills
2. **Document**: Create architecture guide
3. **Test**: Verify hooks work in fresh install
4. **Optional**: Make hooks configurable (some users might not want logging)
5. **Future**: Consider git submodules for shared hooks/skills

---

## 🎓 The Big Picture

```
User's Machine (~/.claude/)
└── agents/              # Global agent definitions (expertise)
    └── python-expert.md

Project Repo (.claude/)
├── commands/            # Project workflows (slash commands)
├── skills/              # Orchestrated workflows (building blocks)
├── hooks/               # Lifecycle events (logging, validation)
├── state/               # Workflow persistence
└── memory/              # Skill learning data

adws/                    # Core Python modules
ai_docs/                 # AI-generated artifacts
specs/                   # Generated specifications
```

**Clean separation**:
- **Global**: Agent personas/expertise
- **Local**: Workflows, automation, data
