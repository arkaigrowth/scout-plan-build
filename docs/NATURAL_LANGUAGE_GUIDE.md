# Scout Plan Build - Natural Language Guide
*Just tell Claude what you want - no syntax required!*

## 🎯 The Big Picture

This framework helps Claude Code build features for you automatically. Think of it as having three assistants:
- **Scout**: Finds relevant files in your codebase
- **Planner**: Creates a detailed implementation plan
- **Builder**: Actually writes the code

## 🗣️ Natural Language Examples (What Actually Works)

### Example 1: Fix a Bug
```
You: "There's a login bug where users can't reset passwords"

Claude will automatically:
1. Scout for authentication files
2. Plan the fix
3. Implement the solution
4. Run tests
5. Create a Bitbucket PR (once we add support)
```

### Example 2: Add a Feature
```
You: "Add a dashboard that shows user statistics"

Claude handles everything:
- Finds existing dashboard code
- Plans the new components
- Builds the feature
- Tests it works
```

### Example 3: Improve Performance
```
You: "The API is slow, optimize the database queries"

Claude will:
- Analyze current queries
- Plan optimizations
- Implement caching/indexing
- Verify improvements
```

## 🚫 What Doesn't Work Yet

### Natural Language Limitations
- ❌ Novel requests: "Add blockchain authentication" (no pattern)
- ❌ Vague requests: "Make it better" (needs specifics)
- ❌ Multiple features: "Add login, dashboard, and API" (do one at a time)

### Technical Limitations
- ❌ Bitbucket: Currently GitHub-only (fixing this week)
- ❌ External docs: Can't fetch documentation reliably
- ❌ Scout phase: 70% broken with external tools

## 📝 When You Need More Control

Sometimes you want to guide the process:

### Option 1: Just the Plan
```
You: "Plan how to add JWT authentication but don't build it yet"
Claude: Creates specs/jwt-auth-plan.md for your review
```

### Option 2: Build from Existing Plan
```
You: "Build the JWT auth from that plan we created"
Claude: Implements specs/jwt-auth-plan.md
```

### Option 3: Skip Testing
```
You: "Add the feature but skip the tests for now"
Claude: Builds without running test suite
```

## 🔧 Behind the Scenes (You Don't Need to Know This)

When you say "Add user profiles", Claude:

1. **Interprets** your request as a feature
2. **Scouts** for files containing "user", "profile", "account"
3. **Plans** based on existing patterns in your code
4. **Builds** following your project's style
5. **Tests** using your existing test framework
6. **Documents** what was changed

All automatic - no commands needed!

## ⚡ Speed Tips

### Make Requests Specific
```
Bad:  "Fix the bug"
Good: "Fix the login timeout bug"
Best: "Fix the bug where users get logged out after 5 minutes"
```

### One Feature at a Time
```
Bad:  "Add login, profiles, and dashboard"
Good: "Add login" → (wait) → "Add profiles" → (wait) → "Add dashboard"
```

### Provide Context
```
Bad:  "Add authentication"
Good: "Add JWT authentication like we discussed, using the existing User model"
```

## 🐛 Troubleshooting

### "I don't see any output"
The framework is working in the background. Check:
- `scout_outputs/` for discovered files
- `specs/` for plans
- `ai_docs/build_reports/` for what was built

### "It's not finding the right files"
Be more specific:
```
Instead of: "Fix the bug"
Try: "Fix the authentication bug in the login controller"
```

### "The plan doesn't look right"
Review and modify:
```
You: "The plan in specs/feature-plan.md needs to also handle admin users"
Claude: Updates the plan accordingly
```

## 🚀 Bitbucket Workflow (Coming Soon)

We're building Bitbucket support. Here's what it will look like:

```
You: "Fix the payment processing bug"

Claude will:
1. Create feature branch
2. Implement the fix
3. Run your tests
4. Create Bitbucket PR with:
   - Proper description
   - Links to issue
   - Test results

You just review and merge!
```

## 💡 Pro Tips

### Let Claude Infer
Don't specify technical details unless needed:
```
Don't say: "Use the Task tool with explore subagent to find auth files"
Just say:  "Find the authentication code"
```

### Trust the Process
The framework knows your codebase:
```
Don't say: "Look in src/controllers/auth.js for the login function"
Just say:  "Fix the login function"
```

### Iterate Naturally
```
You: "Add user profiles"
Claude: [builds basic version]
You: "Add profile pictures to that"
Claude: [enhances with images]
You: "Make the pictures resizable"
Claude: [adds resize feature]
```

## ❓ FAQ

**Q: Do I need to set up environment variables?**
A: Only if running outside Claude Code. Inside Claude, it's automatic.

**Q: Can I use this with Bitbucket?**
A: Not yet (November 2024). GitHub only for now. Bitbucket support in development.

**Q: What if I don't have documentation URLs?**
A: Just skip them! The framework analyzes your code patterns instead.

**Q: How do I know what phase it's in?**
A: Check the latest file timestamps:
- `scout_outputs/` - Scout phase
- `specs/` - Planning phase
- `ai_docs/build_reports/` - Build phase

**Q: Can I interrupt and modify?**
A: Yes! Just tell Claude to stop, modify the plan/code, then continue.

## ✅ Quick Start Checklist

1. ✅ Be specific about what you want
2. ✅ One feature/bug at a time
3. ✅ Let Claude handle the technical details
4. ✅ Review plans before building (optional)
5. ✅ Check outputs in the right directories

## 🎉 That's It!

Just tell Claude what you want in plain English. The framework handles everything else.

No commands. No syntax. No technical knowledge required.

**Ready? Try this:**
```
"Add a health check endpoint to the API that returns the server status"
```

Claude will take it from there! 🚀