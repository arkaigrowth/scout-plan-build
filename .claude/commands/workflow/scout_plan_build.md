---
description: Run scout, plan, and build in sequence for one task. Stops at the first step that fails.
argument-hint: "<task>" [documentation_urls]
---

<!-- risk: mutate-local -->
<!-- auto-invoke: gated -->

# Scout, Plan, Build

Takes one task description and carries it from file discovery to an implemented change.

## Inputs
- `TASK`: $1, the change to make, passed through unchanged to every step
- `DOCS`: $2, optional documentation URLs for the planner

## Steps
1. `/workflow:scout_improved "TASK" "4"`. Keep the path of the `relevant_files.json` it writes.
2. `/planning:plan_w_docs_improved "TASK" "DOCS" "<relevant_files.json path>"`. Keep the spec path under `specs/`.
3. `/workflow:build "<spec path>"`. Keep the build report.

Quote every argument; turn nested double quotes into single quotes.
If a step errors or returns nothing usable, stop there and report which step failed and why. Do not continue to the next step on a guess.

## Report
- Scout: number of files found and the output path
- Plan: spec path and a two-line summary of the approach
- Build: files changed, `git diff --stat`, and anything left undone
