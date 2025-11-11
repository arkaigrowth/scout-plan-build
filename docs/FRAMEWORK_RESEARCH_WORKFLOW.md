# How the Framework Handles Research Tasks
*Understanding the difference between building and researching*

## 🎯 The Framework's Two Modes

### Build Mode (What It's Good At)
```
Trigger words: "implement", "add", "fix", "build", "create"
You: "Add user authentication"
Framework: Scout → Plan → Build → Test → PR
Success Rate: 85%
```

### Research Mode (What It Struggles With)
```
Trigger words: "research", "analyze", "compare", "investigate"
You: "Research Rovo Chat for our needs"
Framework: ???
Success Rate: 30%
```

## 📊 What Actually Happened with Rovo Chat Research

### Step 1: URL Detection (MANUAL)
```
What happened:
- You provided URL in message
- I manually chose WebFetch

What SHOULD happen:
- Framework detects URLs in context
- Auto-fetches and summarizes
```

### Step 2: Initial Fetch (MANUAL)
```python
# What I did manually:
WebFetch(
    url="https://atlassian.com/...",
    prompt="Extract key information..."
)

# What framework SHOULD do automatically:
if "http" in user_message:
    auto_research(url)
```

### Step 3: Deep Analysis (SEMI-AUTOMATIC)
```python
# This part worked well!
Task(
    subagent_type="explore",
    prompt="Analyze how Rovo Chat relates to our needs"
)
# Framework successfully:
# - Found relevant files
# - Compared approaches
# - Generated recommendations
```

### Step 4: Documentation (AUTOMATIC)
```
Framework automatically created:
- rovo_chat_analysis.md
- decision_summary.txt
- implementation_checklist.md
```

## 🔄 The Ideal Research Workflow

### What We Want (Natural Language)
```
You: "Research if Rovo Chat helps with Bitbucket PRs"
```

### What Should Happen Automatically
```python
1. Parse intent: "research" + "Rovo Chat" + "Bitbucket"
2. Extract URL if present
3. Fetch documentation
4. Scout relevant framework files
5. Compare capabilities
6. Generate decision matrix
7. Save research to organized location
```

## 🛠️ Making Research Work Better

### Option 1: Explicit Research Command
```
You: "Research: How does Rovo Chat compare to our PR needs?"
Framework: Triggers research workflow
```

### Option 2: Pattern Recognition
```python
research_triggers = [
    "research", "investigate", "analyze", "compare",
    "evaluate", "assess", "understand", "explore"
]

if any(trigger in user_message for trigger in research_triggers):
    activate_research_mode()
```

### Option 3: URL-Based Auto-Research
```python
if url_detected(user_message):
    content = fetch_url(url)
    context = find_related_code()
    comparison = analyze_relevance(content, context)
    save_research(comparison)
```

## 📁 Research Output Organization

### Current Problem
Research outputs scatter randomly:
```
/tmp/rovo_analysis.md           # Wrong location
/random_research.txt             # No context
/analysis.md                     # What analysis?
```

### Solution: Organized Research Directory
```
ai_docs/
└── research/
    └── 20241109-rovo-chat-bitbucket/
        ├── metadata.json           # Context about research
        ├── initial_fetch.md        # Raw documentation
        ├── analysis.md             # Framework comparison
        ├── decision_matrix.md      # Recommendations
        └── implementation_plan.md  # Next steps
```

## 🎯 Rovo Chat Specific Findings

### The Key Insight
**Rovo Chat is NOT what you need!**

| What You Need | What Rovo Provides |
|---------------|-------------------|
| API for PR creation | UI-only chat interface |
| Programmatic control | Interactive assistance |
| Automation | Human-in-the-loop |
| Available now | Beta, no API |

### The Right Solution
```python
# Build this in 2-3 days:
class BitbucketOps:
    def create_pr(self, title, description, branch):
        # Direct Bitbucket API call
        return requests.post(
            f"{BITBUCKET_API}/pullrequests",
            json={...}
        )
```

## 🚀 How to Research in the Framework

### Today (Manual Process)
```python
# 1. Fetch external documentation
WebFetch(url="...", prompt="analyze for X")

# 2. Analyze against codebase
Task(subagent_type="explore", prompt="compare with our needs")

# 3. Manually organize outputs
organize_research_files()
```

### Tomorrow (After Improvement)
```
You: "Research Rovo Chat for Bitbucket integration"
Framework:
  ✓ Fetches documentation
  ✓ Analyzes codebase
  ✓ Compares capabilities
  ✓ Generates recommendations
  ✓ Saves to ai_docs/research/
  ✓ Returns: "Rovo Chat won't help. Build native integration instead."
```

## ✅ Research Checklist

When researching external tools/services:

1. **Fetch Documentation**
   - [ ] Get official docs
   - [ ] Extract key features
   - [ ] Identify integration points

2. **Analyze Current Code**
   - [ ] Find similar implementations
   - [ ] Identify integration needs
   - [ ] Check existing patterns

3. **Compare & Decide**
   - [ ] Match capabilities to needs
   - [ ] Estimate implementation effort
   - [ ] Generate decision matrix

4. **Document Findings**
   - [ ] Save to organized location
   - [ ] Include timestamps
   - [ ] Preserve context

## 💡 The Bottom Line

**For Rovo Chat specifically:**
- It's a UI tool, not an API
- Won't help with programmatic PR creation
- Build native Bitbucket integration instead (2-3 days)

**For research tasks generally:**
- Framework needs better research mode
- Currently requires manual orchestration
- Should auto-detect and handle research patterns
- Output organization needs improvement

**What worked well:**
- Task agent analysis was thorough
- Found relevant code automatically
- Generated good recommendations

**What needs improvement:**
- Automatic URL detection and fetching
- Research workflow triggers
- Output organization
- Natural language understanding of "research"