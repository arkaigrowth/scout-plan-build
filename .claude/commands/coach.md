---
name: coach
description: Toggle Coach mode for transparent AI workflow visibility
arguments:
  - name: action
    description: "Action: on, off, minimal, full, show, help (default: toggle)"
    required: false
---

# Coach Mode Controller

Toggle transparent AI workflow coaching. Shows decision-making, tool choices, and progress.

## Usage

```
/coach           → Toggle on/off
/coach minimal   → Symbol-only mode (~5% overhead)
/coach full      → Maximum detail (~30% overhead)
/coach show      → Display current mode
/coach help      → Show this help
```

## Mode Comparison

| Mode    | Overhead | Best For                          |
|---------|----------|-----------------------------------|
| off     | 0%       | Speed priority, familiar tasks    |
| minimal | ~5%      | Light visibility, efficiency      |
| on      | ~15%     | Balanced learning and doing       |
| full    | ~30%     | Deep understanding, debugging     |

## What Each Mode Shows

### Off (Default)
Standard Claude output. No coaching overlays.

### Minimal (~5%)
```
🎯 Goal | 📍 1/4
📍 2/4 → ⚙️ Grep... ✅ (12 files)
📍 3/4 → Implementing... 🔄
✅ Done | 3 files | 💡 Add tests
```

### On/Balanced (~15%)
- Journey boxes at task start
- Decision points with options
- Brief tool insights
- Progress at milestones
- Completion summaries

### Full (~30%)
- Complete decision analysis
- All alternatives considered
- Every tool choice explained
- Learning callouts
- Comprehensive summaries

## Action: $ARGUMENTS.action

{{#if (eq ARGUMENTS.action "help")}}
Showing help (above). Use `/coach [mode]` to change.
{{else if (eq ARGUMENTS.action "show")}}
Check current coach mode setting and display status.
{{else if (eq ARGUMENTS.action "minimal")}}
Activate coach-minimal output style. Symbol-only transparency.
Apply the patterns from `~/.claude/output-styles/coach-minimal.md`
{{else if (eq ARGUMENTS.action "full")}}
Activate coach-full output style. Maximum transparency.
Apply the patterns from `~/.claude/output-styles/coach-full.md`
{{else if (eq ARGUMENTS.action "off")}}
Deactivate coach mode. Return to standard output.
{{else if (eq ARGUMENTS.action "on")}}
Activate balanced coach mode.
Apply the patterns from `~/.claude/output-styles/coach.md`
{{else}}
Toggle coach mode. If currently off, activate balanced mode.
If currently on, deactivate.
{{/if}}

## Quick Reference

| Symbol | Meaning           |
|--------|-------------------|
| 📍     | Current position  |
| 🎯     | Goal              |
| 🤔     | Decision point    |
| 💡     | Insight           |
| ⚙️     | Tool usage        |
| 📊     | Progress          |
| ✅❌⚠️ | Status            |
| →»     | Flow              |
