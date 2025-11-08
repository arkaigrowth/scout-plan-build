# AI Documentation Organization Structure

## ✅ The New Structure (Implemented)

```
ai_docs/                      # ALL AI-generated artifacts
├── scout/                    # Scout exploration outputs
│   └── relevant_files.json   # Main scout output
├── build_reports/            # Build phase reports
├── analyses/                 # System analyses
├── reviews/                  # Code reviews
├── architecture/             # Architecture documentation
└── reference/                # Reference guides

specs/                        # AI-generated specifications (separate for visibility)
```

## 🎯 Why This is Better

### Before (Scattered)
```
scout_outputs/          # What outputs? From what?
agents/                 # Agents or agent outputs? Confusing!
ai_docs/               # Some AI docs
specs/                 # More AI docs
```

### After (Organized)
```
ai_docs/               # EVERYTHING AI-generated (except specs)
└── scout/            # Clear: scout's outputs go here
specs/                # Specs stay separate for workflow visibility
```

## 📋 Organizational Principles

1. **Group by Origin**: AI-generated content stays together
2. **Clear Naming**: `ai_docs/scout/` is unambiguous
3. **Workflow Clarity**: Each phase has its place:
   - Scout → `ai_docs/scout/`
   - Plan → `specs/`
   - Build → `ai_docs/build_reports/`
4. **Gitignore Friendly**: Can exclude all AI content with `ai_docs/`

## 🔄 Migration Completed

| Old Path | New Path | Why Better |
|----------|----------|------------|
| `scout_outputs/` | `ai_docs/scout/` | Groups AI artifacts together |
| `agents/scout_files/` | `ai_docs/scout/` | Eliminates confusion with agent definitions |
| Scattered AI docs | `ai_docs/*` | Single source of truth for AI content |

## 📝 Updated References

All code has been updated to use the new structure:
- ✅ `adws/scout_simple.py` - saves to `ai_docs/scout/`
- ✅ All scout commands - use `ai_docs/scout/`
- ✅ Validation scripts - check `ai_docs/scout/`
- ✅ Installer - creates proper structure
- ✅ Documentation - reflects new paths

## 🚀 For New Repos

When installing to other repos (like tax-prep), they'll get:
```
your-repo/
├── ai_docs/
│   ├── scout/         # Scout finds files here
│   ├── build_reports/ # Build saves reports here
│   └── analyses/      # Other AI analyses
└── specs/            # Plans go here
```

This structure is:
- **Self-documenting**: Names explain purpose
- **Consistent**: Same pattern everywhere
- **Scalable**: Easy to add new AI artifact types
- **Clean**: No confusion about what goes where

## 💡 Best Practice

**Rule**: If AI generated it, it goes in `ai_docs/` (except specs which need visibility)

This makes it crystal clear:
- Human code: `src/`, `app/`, etc.
- AI artifacts: `ai_docs/`
- AI specs: `specs/` (for workflow reasons)