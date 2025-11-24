---
description: Execute the ADW Python build script to implement a plan. Preferred build command for spec files in specs/.
argument-hint: <plan_file_path>
---

<!-- risk: mutate-local -->
<!-- auto-invoke: gated -->

# Build (ADW Runner)

# Purpose
Run the ADW Python shim to apply the plan and produce a build report.

# Variables
PLAN_FILE_PATH: $1

# Instructions
- Use Task→Bash to invoke:
  uv run adws/adw_build.py "[PLAN_FILE_PATH]"
- On success, capture the returned path (stdout) to the build report.
- If adw_build.py reports missing "Implementation Steps", stop and notify the user to refine the plan.
