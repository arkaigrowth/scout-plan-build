# Scout-Plan-Build Framework: 10-Minute Deep Dive
## NotebookLM Podcast Script

---

**[Host 1]:** Alright, so we're diving deep today on Scout-Plan-Build. And I gotta say, after reading through this codebase, I'm kind of impressed.

**[Host 2]:** Kind of? That's high praise from you.

**[Host 1]:** Listen, I've seen a lot of "AI framework" projects that are basically just a README and some wishful thinking. But this one? It has receipts.

**[Host 2]:** Okay, set the stage for people. What IS Scout-Plan-Build, from first principles?

**[Host 1]:** So imagine you're working with Claude Code - Anthropic's CLI for Claude. Powerful tool, right? You can ask it to build features, refactor code, analyze bugs. But here's the thing: without structure, it's chaos. You get files dumped in random places, conversations that lose context, no way to resume after a break.

**[Host 2]:** Classic AI assistant problems.

**[Host 1]:** Exactly. So Scout-Plan-Build is like... imagine if you gave Claude a project management system specifically designed for code. It enforces this three-phase workflow: Scout discovers relevant files, Plan creates a specification, Build implements from that spec.

**[Host 2]:** Why three phases? Why not just "build the thing"?

**[Host 1]:** Because that's how chaos happens! Think about how you actually work on a codebase. You don't just start editing random files. You first explore - "where does authentication live?" Then you plan - "okay, I'll modify these three files, add this new endpoint, update these tests." THEN you build.

**[Host 2]:** Okay that makes sense. Separation of concerns.

**[Host 1]:** Right! And here's where it gets interesting - the framework actually has this philosophy baked in. There's a line in their docs: "Commands are deterministic. The LLM suggests, user decides, command executes predictably."

**[Host 2]:** Ooh, I like that. The AI doesn't go rogue.

**[Host 1]:** Exactly. So let's talk about those commands. They've got 48 slash commands organized into functional groups. Planning commands like `/plan_w_docs_improved` and `/planning:feature`. Building commands like `/workflow:build_adw`. Git operations like `/git:commit` and `/git:pull_request`.

**[Host 2]:** Wait, it can create pull requests?

**[Host 1]:** Yeah! And not just basic ones. It analyzes all your commits, generates a summary, creates a test plan, formats it properly, pushes to GitHub. The whole thing.

**[Host 2]:** That's... okay that's actually really useful. What about these parallel worktrees I keep hearing about?

**[Host 1]:** Oh man, this is my favorite feature. So you know how sometimes you're not sure which approach to take? Like, "should we use Redis for caching or just in-memory LRU?"

**[Host 2]:** Yeah, and normally you'd just pick one and hope for the best.

**[Host 1]:** Or waste hours prototyping both! But with Scout-Plan-Build, you run `/git:init-parallel-worktrees cache-strategy 3`. It creates three separate git worktrees - completely isolated working directories.

**[Host 2]:** So you can try three different solutions simultaneously?

**[Host 1]:** Exactly! Each worktree gets the same spec, but implements it differently. Then you run `/git:compare-worktrees` to see stats on all three - lines changed, test coverage, whatever metrics you care about. Pick the best one, merge it with `/git:merge-worktree`, done.

**[Host 2]:** That's like running your own coding competition.

**[Host 1]:** It really is! And it's surprisingly fast because of how they handle parallelization. They measured 40-50% speedup compared to sequential execution.

**[Host 2]:** How'd they measure that?

**[Host 1]:** There's actually a benchmarks directory in the repo. They timed the full workflow - test, review, document phases - running sequentially versus in parallel. Sequential took 12-17 minutes, parallel took 8-11 minutes.

**[Host 2]:** Show me the receipts. I love it.

**[Host 1]:** Right? But here's what really sold me - this thing called dependency-tracer. It's what they call a "high-leverage skill."

**[Host 2]:** Okay, explain high-leverage. That sounds like corporate buzzword bingo.

**[Host 1]:** No, hear me out. Their definition is actually good: "Instead of manually tracing dependencies across 100 files for 2 hours, run a single command for 5 seconds." It's about automating expert work.

**[Host 2]:** Okay, I'm listening.

**[Host 1]:** So normally, if you want to analyze all the imports in a Python codebase - like, really analyze them, validate they exist, check for broken references - you'd load all those files into context. For a 100-file project, that's easily 50,000 tokens.

**[Host 2]:** That's expensive. And Claude has token limits.

**[Host 1]:** Exactly! So dependency-tracer uses this architecture they call "data producer, not context consumer." The Python scripts do the heavy lifting - they use ast-grep and ripgrep to trace all imports, validate them, build dependency graphs. But then instead of dumping all that data into Claude's context...

**[Host 2]:** They summarize it?

**[Host 1]:** Better! They create three output modes. Minimal mode is just counts - "found 316 valid imports, 8 broken." That's like 100 tokens. Summary mode shows you the broken ones with details - maybe 500 to 2,000 tokens. Full mode has everything but you never load it unless you're in what they call a "fix conversation."

**[Host 2]:** Fix conversation?

**[Host 1]:** Yeah, it's like spawning a sub-agent. The main conversation sees "8 broken imports." Then for each broken import, you spawn a separate conversation that loads JUST that import's data - about 300 tokens. Fixes it. Documents the fix. Done.

**[Host 2]:** So 100 tokens for main summary, plus 8 times 300 for fixes...

**[Host 1]:** That's 2,500 tokens total versus 50,000. That's 95% savings!

**[Host 2]:** Okay but here's my question - why should I care about token savings? Tokens are cheap.

**[Host 1]:** Two reasons. One, it's not just cost, it's speed. Fewer tokens means faster responses. And two, you've got context limits. Claude Code defaults to 8,192 output tokens. You blow through that with a dependency dump and suddenly you're hitting errors.

**[Host 2]:** Ah, so it's actually a practical limitation.

**[Host 1]:** Exactly. And here's the cool part - dependency-tracer also generates ASCII diagrams. Like, actual visual dependency trees in your terminal.

**[Host 2]:** Okay you lost me. ASCII diagrams?

**[Host 1]:** Listen, I know it sounds retro, but look at this output:

```
Total Imports: 324
├─ ✓ Valid: 316 (97%)
└─ ✗ Broken: 8 (2%)

├─ ✓ adw_build.py (13 imports, 0 broken)
│  ├─ ✓ sys [import] (installed)
│  └─ ✓ adw_modules.state [from] (local)
└─ ✗ adw_fix.py (8 imports, 1 broken)
   └─ ✗ missing_module [from] (BROKEN)
```

**[Host 2]:** Oh. That's actually... that's really readable.

**[Host 1]:** Right? It's like health bars for your codebase. You can instantly see what's broken and where.

**[Host 2]:** Okay I'm convinced on dependency-tracer. What else makes this framework tick?

**[Host 1]:** Coach mode! This is the learning tool. So by default, Claude just does the work. But if you run `/coach`, suddenly you get this transparent view into its thinking.

**[Host 2]:** Like showing its work in math class?

**[Host 1]:** Exactly! You get journey boxes that show progress:

```
┌─────────────────────────────────────────────┐
│ 📍 Journey: Implement OAuth2                │
│ [▶ Scout] → [Plan] → [Build] → [Test]      │
│ 🎯 Goal: Add OAuth2 login flow             │
└─────────────────────────────────────────────┘
```

**[Host 2]:** Those little progress bars are strangely satisfying.

**[Host 1]:** And you get decision points where it explains trade-offs. Like:

```
🤔 Decision: Which auth library?
   Option A) passport.js - Popular, more setup
   Option B) next-auth - Simpler, Next.js only
   → Choosing: B (matches your stack)
```

**[Host 2]:** So you're learning WHY it makes choices, not just watching code appear.

**[Host 1]:** Exactly! And coach mode has three levels. Minimal is about 5% token overhead, just symbols. Balanced is 15%, nice formatting. Full is 30% but you see everything.

**[Host 2]:** That's thoughtful. Not everyone wants the same level of detail.

**[Host 1]:** Right. And it's all controlled by output styles - you can customize them if you want different formatting.

**[Host 2]:** Okay, let's talk about the workflow. Walk me through an actual example.

**[Host 1]:** Sure. Say you want to add two-factor authentication to your login system. If you're using the natural language interface - which is the recommended way - you just say: "Add 2FA support to the login flow."

**[Host 2]:** That's it?

**[Host 1]:** Claude automatically figures out the workflow. It scouts for auth-related files using Grep or Glob. Finds maybe auth.py, middleware.py, routes.py. Then it runs `/plan_w_docs_improved` with those files, creates a spec in `specs/issue-001-2fa-support.md`.

**[Host 2]:** So the spec is a markdown file?

**[Host 1]:** Yeah! And it's detailed. Requirements, approach, files to modify, testing strategy. It's like a mini design doc. Then Claude runs `/workflow:build_adw` with that spec path, and that's where the magic happens.

**[Host 2]:** What does build_adw do?

**[Host 1]:** It's the core build command. It reads the spec, implements all the changes, creates atomic git commits as it goes, runs tests, generates a build report. And because it's working from a spec, it stays focused. No scope creep.

**[Host 2]:** Okay but what if I want more control?

**[Host 1]:** Then you use slash commands directly! You manually grep for files, review them, call `/plan_w_docs_improved` with specific parameters, then `/workflow:build_adw`. You're in the driver's seat.

**[Host 2]:** Best of both worlds - automation when you want it, control when you need it.

**[Host 1]:** Exactly. And there are commands for everything. `/sc:analyze` for code review across quality, security, performance domains. `/sc:test` runs your test suite. `/testing:test_e2e` for end-to-end browser tests with Playwright.

**[Host 2]:** Wait, it integrates with Playwright?

**[Host 1]:** Yeah! You can run full browser automation tests, take screenshots, validate accessibility. All from slash commands.

**[Host 2]:** This is starting to feel less like a framework and more like an entire development environment.

**[Host 1]:** That's kind of the point! They've got session management commands too. `/session:prepare-compaction` before you take a break, `/session:resume` when you come back. It creates handoff documents that capture your context.

**[Host 2]:** So you don't lose your place?

**[Host 1]:** Exactly. And all the output goes to canonical locations. Specs go in `specs/`. Build reports in `ai_docs/build_reports/`. Reviews in `ai_docs/reviews/`. Nothing scattered around.

**[Host 2]:** Organization. Structure. Determinism. These words keep coming up.

**[Host 1]:** Because that's the core philosophy! Look at their rules - they've got behavioral rules in the framework. Things like "Build ONLY what's asked" to prevent scope creep. "No partial features" - if you start implementing, you must complete it. "No TODO comments" - real code only.

**[Host 2]:** Huh. So it's enforcing discipline on the AI?

**[Host 1]:** And on you! One rule is "Git Safety: ALWAYS create feature branch before changes." Another is "Root cause analysis: never skip tests to achieve results."

**[Host 2]:** These sound like they came from painful experience.

**[Host 1]:** Oh absolutely. And here's the kicker - this framework was built using itself. It's totally dogfooded.

**[Host 2]:** So the specs that built the framework...

**[Host 1]:** Are in the repo! You can see the actual Scout-Plan-Build workflow applied to Scout-Plan-Build. It's recursive.

**[Host 2]:** That's either brilliant or slightly terrifying.

**[Host 1]:** Why not both? But seriously, it means the framework is validated through use. Every feature went through scout → plan → build. Every optimization was tested.

**[Host 2]:** What about edge cases? What if I have like 50 files to change?

**[Host 1]:** They've got decision helpers in the docs. 1-3 files? Just do it directly. 4-10 files? Use plan → build. 11+ files? Parallel worktrees. It's about matching the right tool to the scope.

**[Host 2]:** And if requirements aren't clear?

**[Host 1]:** Then you start with `/sc:analyze` or `/sc:design` to understand the problem space first. Or you use parallel worktrees to try multiple approaches.

**[Host 2]:** This is surprisingly well thought out.

**[Host 1]:** I know, right? And installation is actually painless. Run one install script, it creates the directory structure alongside your existing code. Doesn't touch your files.

**[Host 2]:** What gets installed?

**[Host 1]:** The `adws/` directory with core modules. The `.claude/commands/` directory with all 48 slash commands. Directory structure for specs, scout outputs, AI docs. That's it.

**[Host 2]:** And to use it?

**[Host 1]:** Add your Anthropic API key to `.env`, set some environment variables like `CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768` to prevent token limit errors, and you're done. Five minutes tops.

**[Host 2]:** Okay, real talk - what are the limitations? What doesn't work?

**[Host 1]:** Great question. According to their status page, the Scout slash commands are only 40% working. They recommend using native Grep and Glob tools instead.

**[Host 2]:** So file discovery is manual?

**[Host 1]:** Or use natural language and let Claude figure it out. But yeah, the `/scout` commands are partially broken. They're transparent about it.

**[Host 2]:** I appreciate honesty. What else?

**[Host 1]:** Portability is 85%. Some paths are still hardcoded. They're working on it. And the plan/build commands are 80% - working but need more validation.

**[Host 2]:** So it's actively being developed?

**[Host 1]:** Yeah, it's version 4.0 of their MVP. Last updated November 24th, 2025. Recent commits show they're adding features, fixing issues, improving docs.

**[Host 2]:** Who's building this?

**[Host 1]:** That's not totally clear from the repo, but it seems like a small team that's serious about structured AI development. The code quality is solid, documentation is thorough, and they're clearly using it themselves.

**[Host 2]:** Alright, pitch me. Why should someone actually use this versus just raw Claude Code?

**[Host 1]:** Three reasons. One, structure without ceremony. You get organized workflows without drowning in process. Two, token efficiency matters. Tools like dependency-tracer give you 100x leverage - 5 seconds instead of 2 hours, 3,000 tokens instead of 60,000. Three, it's a learning tool. Coach mode teaches you how to think about code changes systematically.

**[Host 2]:** Who's it for?

**[Host 1]:** Anyone doing serious work with AI coding assistants. If you're just fixing a typo, you don't need this. But if you're building features, refactoring systems, onboarding to new codebases? This framework pays for itself immediately.

**[Host 2]:** And the learning curve?

**[Host 1]:** Ironically pretty gentle. Start with natural language - just describe what you want. The framework handles routing to the right commands. As you get comfortable, you can use slash commands directly for more control. Then eventually you might write custom skills or extend the framework.

**[Host 2]:** Progressive disclosure of complexity.

**[Host 1]:** Exactly! And with coach mode on, you're learning the whole time.

**[Host 2]:** Okay, I'm sold. Where do we send people?

**[Host 1]:** The repo is public. Installation takes five minutes. And honestly? Just try the dependency-tracer first. Even if you don't use the full framework, that tool alone is worth it.

**[Host 2]:** 95% token savings is 95% token savings.

**[Host 1]:** Right? And those ASCII diagrams are genuinely useful. Health bars for your imports.

**[Host 2]:** I still can't believe ASCII is cool again.

**[Host 1]:** Everything old is new again! But seriously, this framework represents something important. AI coding assistants are incredibly powerful, but without structure, they're chaos. Scout-Plan-Build proves you can add structure without killing flexibility.

**[Host 2]:** Deterministic workflows that actually ship.

**[Host 1]:** That's the tagline! And it's earned. This thing actually works.

**[Host 2]:** Alright, I'm convinced. Scout-Plan-Build - bringing order to AI chaos.

**[Host 1]:** Now go build something structured.

---

**Total Time:** ~10 minutes
**Tone:** In-depth but conversational, technical but accessible
**Key Points Covered:**
- Core philosophy (deterministic, LLM suggests/user decides)
- All three phases explained (Scout/Plan/Build)
- 48 slash commands overview
- Parallel worktrees in detail (killer feature)
- dependency-tracer deep dive (architecture, token savings, ASCII diagrams)
- Coach mode and learning features
- Actual workflow examples
- Session management
- Canonical locations and organization
- Behavioral rules and discipline
- Dogfooding (built with itself)
- Installation and setup
- Honest limitations (Scout 40%, portability 85%)
- Who it's for and why it matters
- Progressive learning curve
