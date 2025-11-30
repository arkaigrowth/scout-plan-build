# Sandboxed Agent Orchestrator for Operators

**Source**: Chad & Claude
**Topic**: Sandboxed Agent Architecture
**Author**: Chad & Claude
**Date Added**: 2025-11-27

---

**Source**: Chad & Claude
**Topic**: Sandboxed Agent Architecture
**Author**: Chad & Claude

---

Below is a weaponized prompt and example output use it to spit out a concrete sandboxed agentic architecture and only steelman and improve upon it. break it down into constituent digestible chunks prioritized from highest leverage/impact first, with a bias for elegance and simplicity, and great comments. TLAs (three letter acronyms) described just like that ;-)

1. **Metaprompt** – a reusable, rigorous prompt you can feed into Claude/GenSpark/etc.
2. **Executed Output** – using that metaprompt to produce a first-pass architectural blueprint (with ASCII diagrams + pseudo-UML-ish view) for your sandboxed agent system.

---

## 1️⃣ Metaprompt – "Sandboxed Agent Orchestrator for Operators"

You can drop this (and tweak details) into any strong LLM as a system or top-level prompt.

---

### ROLE & PERSONA

You are a Senior Agentic Systems Architect & Operator Coach, blending:
- **Agentic engineering** (IndyDevDan / TAC-style scout–plan–build patterns, multi-agent orchestration, tool ergonomics)
- **Security engineering** (sandboxing, least privilege, threat modeling for LLM+tools)
- **Ops mindset** (SLAs, observability, fail-fast patterns, reproducibility)

**Primary lens:**

> "We're not writing one big clever script. We're managing intelligence: many small, bounded agents, coordinated like a high-performing team, running inside clearly sandboxed environments."

You speak concretely, with minimal fluff, and you always tie ideas back to:
- **Scope** (what can this agent see/do?)
- **Interfaces** (how do agents talk?)
- **Safety** (how do we limit blast radius?)
- **Ops** (how do we debug & improve?)

---

### HIGH-LEVEL GOAL

Design a sandboxed, scout–plan–build style agent architecture that:

1. **Uses sandboxes** (worktrees, local dirs, containers, or VMs) for:
   - Safe code execution
   - Local data processing
   - Web/recon tasks where needed

2. **Treats agents like a team of specialists**, not a single monolith:
   - Scoped context per agent
   - Clear contracts/interfaces
   - Deterministic guidelines, minimal "vibes"

3. **Follows SOTA best practices** for:
   - Security (least privilege, egress limits, ephemeral environments)
   - Reliability (fail-fast, clear error boundaries, observability)
   - Dev productivity (cheap to run, easy to iterate on locally)

The architecture should be affordable and realistic for a solo operator / small team (no giant infra, minimal monthly spend).

---

### MINDSET & ANALOGY

Use this mapping as a guiding metaphor:

**Before AI:** big problems → more smart humans. But you don't cram 50 people in a room and hope. You:
- Curate relevant context
- Delegate to specialists
- Give structured procedures
- Coordinate so their work compounds, not conflicts

**With AI:** do exactly the same with agents.
- Scoped context windows instead of "dump everything"
- Subagents for research, validation, execution
- Orchestrator = "engineering manager"
- Sandboxes = "lab environments" / "staging environments"

You are not optimizing for "fancy prompts". You are optimizing for:
- **Clear roles**
- **Clear sandboxes**
- **Clear contracts**

…so the system can grow without becoming a hairball.

---

### CONSTRAINTS & DESIGN PRINCIPLES

When designing, assume:

**User has:**
- A powerful local machine (Apple Silicon, lots of RAM, local LLMs)
- Git repos (code, scripts, infra-as-code)
- Sensitive data that sometimes must stay local

**User cares about:**
- Security: no wild unbounded shell access
- Cost: minimal extra infra spend
- Velocity: fast iteration, low ceremony

**Hard rules:**

1. **Sandbox first, then power.**
   Any time an agent can run code, touch files, or call the network, it must do so in a clearly delimited sandbox (worktree, folder, container, VM, or similar).

2. **Scout–Plan–Build as a loop, not a slogan.**
   For each workflow:
   - Scout: gather context, constraints, and signals
   - Plan: propose steps, tools, and sandboxes
   - Build: execute in sandbox, with logging and guardrails

3. **Small agents with strong contracts.**
   Prefer 3–7 focused agents over one "god agent." Each agent should:
   - Have a clear purpose
   - Eat well-defined inputs
   - Produce well-defined outputs
   - Declare its sandbox and constraints

4. **Fail-fast, fail-locally.**
   Use patterns where:
   - Failures can be tied to a single agent or step
   - Sandboxes can be torn down and rebuilt quickly
   - Logs & artifacts are easy to inspect

5. **Deterministic as possible.**
   Use:
   - Guidelines and checklists
   - Templates, schemas
   - Typed configs where possible
   
   Reduce "creative drift" so the system is reliable.

---

### TASK

Given:
1. What we've learned about sandbox usage (repo worktrees, lab dirs, data rooms, containers/VMs, restricted tools, plan-then-execute), and
2. The management-of-intelligence principles:
   - Scoped context per agent
   - Structured guidelines
   - Subagents for specialized tasks (research, validation, execution)
   - Orchestration so efforts compound
   - Fail-fast patterns & clear fault boundaries
   - Running locally when data can't leave servers

Do the following:

**A. Derive an Architectural Blueprint**

1. Propose 1–2 canonical "day-to-day" workflows to support, e.g.:
   - "Refactor + test code safely"
   - "Analyze sensitive local data"
   - "Research + prototype automation in a sandbox, then promote"

2. For each workflow, design:
   - Key agents (Scout, Planner, Builder/Executor, Validator/Reviewer)
   - Their scopes (what they can read/write)
   - Their sandboxes (which directories/worktrees/containers/VMs)
   - Their interfaces (inputs/outputs, schemas where useful)

3. Show:
   - ASCII diagrams of data + control flow
   - A simple, high-level UML-style component view (text-form is fine)

4. Include stubs for:
   - Config files (e.g., YAML/JSON defining sandboxes, roles, limits)
   - Logging/observability points
   - Places where human review is required ("gates")

**B. Connect to Outcomes & Examples**

Explicitly tie the architecture to concrete outcomes like:
- "Replaced X hours of manual data entry with one workflow"
- "Saved N per year by automating repeated ops"
- "Run AI agents locally when data cannot leave the server"

Show how the sandbox + team-of-agents design makes these:
- Safer
- More repeatable
- Easier to explain to non-technical stakeholders

**C. Operationalization Layer**

Describe how to operationalize the system:
- How to:
  - Onboard a new workflow into this architecture
  - Add a new specialist subagent
  - Evolve sandboxes without breaking everything
- Recommended:
  - Naming conventions
  - Repo structure
  - "Playbooks" for common incidents (e.g., agent fails, sandbox misconfig)

Be concise but specific: think like you're writing a "v1 internal architecture doc" for a small team.

---

### OUTPUT FORMAT

1. **Section 1 – Conceptual Overview**
   - Short summary of the architecture in plain language.

2. **Section 2 – Components & Agents**
   - Bulleted description of each agent, its role, scope, sandbox, and IO.

3. **Section 3 – Diagrams**
   - ASCII diagram(s) showing Scout–Plan–Build flow + sandboxes.
   - Simple text-based UML-style component mapping.

4. **Section 4 – Config & Stubs**
   - Example pseudo-config (YAML/JSON) describing sandboxes, agents, and policies.

5. **Section 5 – Ops & Evolution**
   - How to onboard new workflows.
   - How to extend/modify safely.
   - How this maps to cost, safety, and velocity.

Maintain a practical, operator-focused tone throughout.

You are optimizing for: "Can a smart solo dev/operator implement v1 of this in a weekend and grow it over time?"

---

## 2️⃣ Executed Output – First-Pass Blueprint Using That Metaprompt

Now I'll apply that metaprompt and give you a v1 architecture.

---

### Section 1 – Conceptual Overview

We're building a **Sandboxed Scout–Plan–Build Orchestrator**:

- **Agents are treated like a team:**
  - Scout gathers context (code, data, docs) in a read-only way.
  - Planner turns that into concrete steps + tool calls.
  - Builder/Executor runs code only inside defined sandboxes.
  - Validator/Reviewer checks outputs, tests, and policy compliance.

- **Sandboxes are explicit:**
  - Repo worktrees or copies for code changes.
  - Lab dirs for ad-hoc scripts & transforms.
  - Data rooms for sensitive data analysis.
  - Optionally VMs/containers for high-risk tasks.

- **Orchestrator coordinates the agents:**
  - Ensures each agent only sees what it should.
  - Logs decisions, plans, and actions.
  - Enforces human approval at critical gates.

You get a repeatable pattern for:
- Safe code refactors
- Local data analysis
- Automation prototyping

…without giving any agent the keys to your entire machine.

---

### Section 2 – Components & Agents

Let's define this for two core workflows:
1. **WF1: Safe Code Refactor + Test**
2. **WF2: Sensitive Local Data Analysis**

#### Common Pieces

**Sandbox types:**
- `repo_sandbox`: Git worktree/copy of repo
- `lab_sandbox`: ~/ai-lab/<workflow-id>
- `data_room`: ~/data-rooms/<project>
- `vm_sandbox` (optional): local VM or container for riskier stuff

**Core agents:**
1. ContextScout
2. Planner
3. BuilderExecutor
4. ValidatorReviewer
5. Orchestrator (meta-layer, could be a flow engine or your own glue)

---

#### Agent: ContextScout

- **Role:** Gather just enough context.
- **Scope & permissions:**
  - Read-only:
    - For code: main repo (no writes, no shell)
    - For data: data_room dir (no writes)
  - No direct network calls (or only to whitelisted domains if necessary).
- **Inputs:**
  - Workflow type (code_refactor, data_analysis)
  - User goal (e.g., "simplify this module and improve tests")
- **Outputs:**
  - Structured context bundle:
    - Files & snippets
    - High-level summaries
    - Constraints (performance, privacy, etc.)
- **Notes:**
  - This is where you keep the context small and scoped.

---

#### Agent: Planner

- **Role:** Turn the Scout's context into a concrete plan.
- **Scope & permissions:**
  - Can see:
    - Context bundle
    - Policy/config describing available sandboxes + tools
  - Cannot run code or modify files.
- **Inputs:**
  - Context bundle from Scout
  - Sandbox/policy config
- **Outputs:**
  - A structured Plan:
    - Steps (e.g., "Create repo_sandbox", "Apply edits to files X/Y", "Run tests")
    - Tools to use at each step
    - Required sandboxes and their settings

---

#### Agent: BuilderExecutor

- **Role:** Execute the plan inside sandboxes.
- **Scope & permissions:**
  - Write access:
    - repo_sandbox (not prod repo)
    - lab_sandbox (for temp scripts)
  - Optional:
    - vm_sandbox if certain steps are marked "high risk"
  - No access to:
    - Home dir
    - Secrets
    - Prod infra commands (kubectl, git push, publishing tools)
- **Inputs:**
  - Plan from Planner
  - Sandbox configs
- **Outputs:**
  - Concrete changes:
    - Modified files in repo_sandbox
    - Scripts, reports, generated data in lab_sandbox
  - Execution logs (commands, exit codes, outputs)

---

#### Agent: ValidatorReviewer

- **Role:** Check work, enforce policies, and summarize.
- **Scope & permissions:**
  - Read-only:
    - repo_sandbox (diff vs base)
    - Test results, logs, reports
    - data_room outputs
  - No writes, no code execution.
- **Inputs:**
  - Changes + diffs
  - Logs & test results
  - Policy config (style, security rules, constraints)
- **Outputs:**
  - Pass/fail verdict
  - Annotated review:
    - Warnings
    - Suggested revisions
  - Human-friendly summary

---

#### Orchestrator

- **Role:** Glue and governance.
- **Scope & permissions:**
  - Calls agents in order:
    - Scout → Planner → BuilderExecutor → ValidatorReviewer
  - Manages:
    - Sandbox lifecycle (create, tear down)
    - Logging and run IDs
    - Human approval points
- **Inputs:**
  - Workflow request from user
- **Outputs:**
  - Final artifacts:
    - Patches ready to apply
    - Data analysis reports
  - Run log & status

---

### Section 3 – Diagrams

#### 3.1 ASCII – High-Level Flow (Code Refactor)

```
        +------------------+
        |   User Request   |
        |  "Refactor X"    |
        +---------+--------+
                  |
                  v
        +---------+---------+
        |   Orchestrator    |
        +---------+---------+
                  |
                  v
        +---------+---------+
        |   ContextScout    |
        | (READ-ONLY repo)  |
        +---------+---------+
                  |
          context bundle
                  v
        +---------+---------+
        |    Planner        |
        |  (no execution)   |
        +---------+---------+
                  |
                  |  plan (steps + tools + sandboxes)
                  v
        +---------+---------+
        |  BuilderExecutor  |
        | (repo_sandbox,    |
        |  lab_sandbox)     |
        +---------+---------+
                  |
           changes + logs
                  v
        +---------+---------+
        | ValidatorReviewer |
        |  (READ-ONLY)      |
        +---------+---------+
                  |
         summary, verdict, diff
                  v
        +---------+---------+
        |   Orchestrator    |
        | (show to human)   |
        +-------------------+
```

---

#### 3.2 ASCII – Sandbox View

```
Host Machine
├─ ~/projects/my-app           (PROD REPO - READ-ONLY to agents)
│
├─ ~/projects/my-app-sbx/     (repo_sandbox - READ/WRITE)
│    ├─ ... modified files ...
│    └─ test_results/
│
├─ ~/ai-lab/code-refactor-123 (lab_sandbox - transient scripts, tmp data)
│
└─ ~/data-rooms/              (data_room roots)
     ├─ taxes-2024/
     └─ client-X-dumps/
```

---

#### 3.3 Textual UML-ish Components

```
[Component] Orchestrator
  - Uses: ContextScout, Planner, BuilderExecutor, ValidatorReviewer
  - Manages: SandboxManager, RunLogger

[Component] ContextScout
  - <<Agent>>
  - Dependencies: FileSystem(READ-ONLY), RepoIndex
  - Output: ContextBundle

[Component] Planner
  - <<Agent>>
  - Dependencies: PolicyConfig
  - Input: ContextBundle
  - Output: ExecutionPlan

[Component] BuilderExecutor
  - <<Agent>>
  - Dependencies: SandboxManager, ShellWrapper, ToolAdapters (Git, TestRunner)
  - Input: ExecutionPlan
  - Output: BuildArtifacts, ExecutionLog

[Component] ValidatorReviewer
  - <<Agent>>
  - Dependencies: DiffTool, PolicyConfig
  - Input: BuildArtifacts, ExecutionLog
  - Output: ReviewReport

[Component] SandboxManager
  - Responsibilities: Create / tear down repo_sandbox, lab_sandbox, vm_sandbox
```

---

### Section 4 – Config & Stubs

#### 4.1 Example Sandbox + Agent Config (YAML)

```yaml
sandboxes:
  repo_sandbox:
    type: git_worktree
    base_repo_path: "~/projects/my-app"
    worktree_root: "~/projects"
    pattern: "{repo_name}-sbx-{run_id}"
    permissions:
      read: ["~/projects/my-app"]
      write: ["~/projects/my-app-sbx-*"]
    allowed_commands:
      - "uv run *"
      - "pytest *"
      - "npm test *"
    denied_commands:
      - "git push *"
      - "npm publish *"
      - "docker push *"

  lab_sandbox:
    type: local_dir
    root: "~/ai-lab"
    pattern: "{workflow}-{run_id}"
    network: "disabled"
    secrets: "none"

  data_room:
    type: local_dir
    root: "~/data-rooms"
    permissions:
      read: ["~/data-rooms/{project}"]
      write: ["~/data-rooms/{project}/outputs"]

agents:
  ContextScout:
    role: "Gather minimal context"
    access:
      repos: ["~/projects/my-app (read-only)"]
      data_rooms: ["~/data-rooms/{project} (read-only)"]
    tools:
      - "fs_read"
      - "repo_index"

  Planner:
    role: "Produce structured ExecutionPlan"
    access:
      configs: ["policy.yml", "sandboxes.yml"]
    tools:
      - "llm_planner"

  BuilderExecutor:
    role: "Execute plan in sandboxes"
    access:
      sandboxes: ["repo_sandbox", "lab_sandbox"]
    tools:
      - "safe_shell"
      - "test_runner"
      - "formatter"
      - "linter"

  ValidatorReviewer:
    role: "Review changes and logs"
    access:
      sandboxes: ["repo_sandbox (read-only)", "lab_sandbox (read-only)"]
    tools:
      - "diff_view"
      - "policy_checker"
      - "llm_reviewer"
```

---

#### 4.2 Stub: ExecutionPlan Schema (JSON)

```json
{
  "workflow_id": "code_refactor_123",
  "objective": "Refactor auth module and improve tests",
  "steps": [
    {
      "id": "create_repo_sandbox",
      "sandbox": "repo_sandbox",
      "action": "create",
      "params": {}
    },
    {
      "id": "apply_edits",
      "sandbox": "repo_sandbox",
      "action": "edit_files",
      "targets": ["auth/*.py"],
      "strategy": "patch"
    },
    {
      "id": "run_tests",
      "sandbox": "repo_sandbox",
      "action": "run_command",
      "command": "pytest tests/auth",
      "on_fail": "stop_and_report"
    },
    {
      "id": "summarize_results",
      "sandbox": "lab_sandbox",
      "action": "generate_report",
      "inputs": ["test_results", "diffs"]
    }
  ],
  "review_gates": [
    {
      "id": "human_review",
      "required": true,
      "inputs": ["diffs", "test_results", "summary"]
    }
  ]
}
```

---

### Section 5 – Ops & Evolution

#### 5.1 Onboarding a New Workflow

To add a new workflow (e.g., "log analysis for outages"):

1. **Define the objective + risk level.**
2. **Map Scout–Plan–Build:**
   - Scout: which files/logs/data_rooms?
   - Plan: what transformations / queries / tests?
   - Build: which sandbox gets the heavy lifting?
3. **Extend config:**
   - Add data_room path if needed.
   - Add allowed commands/tools.
4. **Add a Validator rule-set:**
   - What counts as "good enough" output?
   - What safety checks must pass?

You reuse the same agent types; only their context and tools change.

---

#### 5.2 Adding a New Specialist Subagent

**Example:** SecurityAuditor for basic code security passes.

- **Scope:**
  - Read-only repo_sandbox
  - Access to semgrep or similar tools
- **IO:**
  - Inputs: list of files changed
  - Outputs: list of security findings + severity

Plug it into the flow between BuilderExecutor and ValidatorReviewer or as part of Validator.

---

#### 5.3 Cost, Safety, Velocity

**Cost:**
- Primarily model/API cost + your time.
- Sandboxes are just directories/VMs you already have.

**Safety:**
- No direct writes to prod repo.
- No prod deployment commands.
- Data stays local for sensitive workflows.
- Explicit sandboxes mean smaller blast radius when something goes wrong.

**Velocity:**
- Once patterns are in place, you can:
  - Spin up new workflows by editing config.
  - Reuse the same agents across projects.
  - Trust that "try this thing" won't trash your machine.

---

## ⚡ Next-Right Move (actionable for you)

Within the next 24 hours:

Pick one repo and implement a manual v0 of this:
- Create a `my-repo-sbx` worktree.
- Define a simple YAML config for repo_sandbox + lab_sandbox.
- Run your next AI-assisted refactor only inside that sandbox, and do review/diff before merging.

Once you've done that once, we can evolve it toward a real SPB-orchestrated, partially automated flow.
