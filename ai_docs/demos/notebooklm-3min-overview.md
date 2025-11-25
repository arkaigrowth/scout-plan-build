# Scout-Plan-Build Framework: 3-Minute Overview
## NotebookLM Podcast Script

---

**[Host 1]:** Okay, so you know what's really annoying about AI coding assistants?

**[Host 2]:** Oh, I can think of a few things...

**[Host 1]:** Right? They're incredibly powerful, but they're also completely chaotic. You ask Claude or ChatGPT to build something, and ten minutes later you've got files scattered everywhere, no idea what just happened, and if you take a break? Good luck picking up where you left off.

**[Host 2]:** Yeah, it's like... the AI has ADHD. Super capable, but zero organization.

**[Host 1]:** Exactly! So that's the problem Scout-Plan-Build solves. It's a framework that gives AI assistants - specifically Claude Code - a deterministic workflow. Like, actually structured.

**[Host 2]:** Deterministic. I like that word. What does that mean in practice?

**[Host 1]:** It means: Scout → Plan → Build. Three steps. Every time. You want to add OAuth to your app? Scout finds all your auth files, Plan creates a specification, Build implements it. Done.

**[Host 2]:** And this runs... automatically?

**[Host 1]:** Here's the cool part - you can just talk to it in natural language. "Add two-factor authentication to the login flow" and it figures out which commands to run. Or if you want control, you use slash commands like `/plan_w_docs_improved` and `/build_adw`.

**[Host 2]:** Wait, slash commands? In Claude?

**[Host 1]:** Yeah! The framework includes 48 slash commands. It's like giving Claude a swiss army knife. You want to analyze code? `/sc:analyze`. Run tests? `/sc:test`. Create three parallel git branches to try different approaches? `/git:init-parallel-worktrees`.

**[Host 2]:** Okay that last one is wild. You're saying it can try multiple solutions at once?

**[Host 1]:** Exactly! Say you're not sure whether to use Redis caching, in-memory LRU, or SQLite for a feature. You spin up three worktrees, each tries a different approach, then you compare results and merge the winner. It's like running your own mini coding competition.

**[Host 2]:** That's... that's actually brilliant. What about this "Coach Mode" thing I saw mentioned?

**[Host 1]:** Oh, Coach Mode is great for learning. It makes Claude's thinking visible. You see journey boxes with progress bars, decision points where it explains trade-offs, tool insights... It's like having Claude narrate what it's doing and why.

**[Host 2]:** So instead of just watching code appear, you're learning the reasoning?

**[Host 1]:** Exactly. And it has three levels - minimal is like 5% overhead with just symbols, balanced is 15% with nice formatting, and full mode is 30% overhead but you see EVERYTHING.

**[Host 2]:** This is starting to make sense. But here's my question - does it actually work? Or is this vaporware?

**[Host 1]:** No, seriously, watch this. There's a tool called dependency-tracer that's part of the framework. Normally, if you want to analyze all the imports in a 100-file Python codebase, that's like 50,000 tokens of context. Huge.

**[Host 2]:** That's expensive and slow.

**[Host 1]:** Right. But dependency-tracer uses this "data producer, not context consumer" architecture. It generates JSON files with all the data, but then only shows you a 100-token summary. "Found 316 valid imports, 8 broken ones." And it even makes ASCII diagrams!

**[Host 2]:** ASCII diagrams in 2025? That's retro.

**[Host 1]:** But it works! You get these visual dependency trees right in your terminal. Health bars showing import status. And if there ARE broken imports, you spawn what they call "fix conversations" - basically mini-agents that each tackle one broken import. So instead of 50,000 tokens, you use like 3,000 total.

**[Host 2]:** Okay that's genuinely clever. 95% token savings is real money.

**[Host 1]:** And real time. Speaking of which - the framework uses parallel execution wherever possible. Testing, reviewing, documenting - they all run simultaneously. They measured 40-50% speedup compared to doing things sequentially.

**[Host 2]:** So what's the catch? Installation nightmare?

**[Host 1]:** Nope. You run one script, it installs alongside your existing code without touching it. Creates directories like `specs/` for specifications, `scout_outputs/` for discovery results, `ai_docs/` for generated docs. Everything has a home.

**[Host 2]:** Canonical locations. I'm sensing a theme here - structure, determinism, organization.

**[Host 1]:** That's the whole point! AI is powerful but chaotic. This framework adds the structure without killing the flexibility. You can use natural language for simple stuff, slash commands for control, or even write your own custom skills.

**[Host 2]:** Okay, I'm sold. How do I try it?

**[Host 1]:** Five minutes. Seriously. Clone the repo, run the install script, add your Anthropic API key. Start with something simple like "find all my authentication files" and watch it work.

**[Host 2]:** And if I want to go deeper?

**[Host 1]:** Then you're in for a treat. Because this whole framework was built using itself. It's dogfooded. The specs that generated the code, the build reports, the session handoffs - they're all in the repo. You can see exactly how structured AI development works in practice.

**[Host 2]:** That's actually beautiful. Recursive improvement.

**[Host 1]:** Right? It's like... what if AI coding assistants grew up and got organized?

**[Host 2]:** Scout-Plan-Build. Structure that actually ships.

**[Host 1]:** Now you're getting it.

---

**Total Time:** ~3 minutes
**Tone:** Conversational, pragmatic, showing real benefits
**Key Points Covered:**
- The problem (chaos)
- The solution (deterministic workflows)
- Natural language + slash commands
- Parallel worktrees (killer feature)
- Coach mode (learning tool)
- dependency-tracer (100x leverage example)
- Token/time savings (concrete numbers)
- Easy 5-minute start
