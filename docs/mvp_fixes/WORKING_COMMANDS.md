# 🚀 WORKING COMMANDS - Use These Right Now!

## The 3-Step Process That Actually Works

### Step 1: Scout (WORKS!)
```bash
# This works perfectly - finds files and sorts them
python adws/scout_simple.py "your task description"

# Example:
python adws/scout_simple.py "add user authentication"
```

Output goes to: `agents/scout_files/relevant_files.json`

### Step 2: Plan (USE SLASH COMMAND)
Since adw_plan.py has argument issues, use the slash command instead:

```bash
# In Claude Code, use:
/plan_w_docs "your task" "docs_url" "agents/scout_files/relevant_files.json"

# Or if slash command doesn't work, manually create a spec:
echo "# Spec for your task" > specs/my-task.md
```

### Step 3: Build (USE SLASH COMMAND)
```bash
# In Claude Code, use:
/build_adw "specs/your-spec.md"

# Or use the Python script directly:
python adws/adw_build.py "specs/your-spec.md"
```

---

## Complete Example (Do This Now!)

```bash
# 1. Scout for files
python adws/scout_simple.py "add health check endpoint"

# 2. Check what was found
cat agents/scout_files/relevant_files.json | head -20

# 3. Use slash command for plan (in Claude Code)
/plan_w_docs "add health check endpoint" "" "agents/scout_files/relevant_files.json"

# 4. Use slash command for build
/build_adw "specs/[whatever-was-created].md"

# 5. Check what changed
git diff

# 6. Commit if happy
git add . && git commit -m "feat: add health check endpoint"
```

---

## Quick Health Check

Run this first to make sure everything's ready:

```bash
python check_health.py
```

---

## If Slash Commands Don't Work

Create a simple spec manually and skip to build:

```bash
# Create minimal spec
cat > specs/my-task.md << 'EOF'
# Task: Add Health Check

## Requirements
- Add /health endpoint
- Return status: ok

## Files to modify
- main.py or app.py
EOF

# Run build on it
python adws/adw_build.py specs/my-task.md
```

---

## What's Actually Working

| Component | Status | Command |
|-----------|--------|---------|
| **Scout** | ✅ 100% Working | `python adws/scout_simple.py "task"` |
| **Plan** | ⚠️ Use slash command | `/plan_w_docs` in Claude Code |
| **Build** | ⚠️ Use slash command | `/build_adw` in Claude Code |
| **Validation** | ✅ Working | Automatic with all commands |
| **State** | ✅ Working | Saved to JSON files |

---

## The Truth

- **Scout**: We fixed it! Uses grep/find instead of broken AI tools
- **Plan/Build**: The slash commands work better than raw Python scripts
- **Everything else**: Already working fine

**Bottom line**: You can use this RIGHT NOW for real tasks. The scout we just created + slash commands = working pipeline.

---

## Need GitHub CLI?

Install it when you get a chance:

```bash
brew install gh
gh auth login
```

But you can use everything else without it!