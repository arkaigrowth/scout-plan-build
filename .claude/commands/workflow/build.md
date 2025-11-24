---
description: Implement changes from a plan file with atomic commits. Returns build report with diff stats.
argument-hint: <plan_file_path>
---

<!-- risk: mutate-local -->
<!-- auto-invoke: gated -->

# Build

# Purpose
Implement changes as specified by the given plan file; produce a succinct build report (diff stats, touched files).

# Variables
PLAN_FILE_PATH: $1

# Workflow
- Read the plan; confirm scope and success criteria.
- Execute changes stepwise; use small atomic commits.
- Capture `git diff --stat` and return a human-readable build report.
- If the plan is ambiguous, stop and report uncertainties.

# Output
- `build_report` (text) with: operations done, files changed, next steps.
