<!-- risk: mutate-local -->
<!-- auto-invoke: gated -->

# Scout Plan Build

# Purpose
Run a three-step engineering workflow to deliver on the `USER_PROMPT`.

First we scout the codebase for files needed to complete the task.  
Then we plan the task based on the files found.  
Then we build the task based on the plan.

# Variables
USER_PROMPT: $1
DOCUMENTATION_URLS: $2

# Instructions
- Execute each step in order, top to bottom.
- If you get an unexpected result, stop and notify the user.
- Place each argument within double quotes (escape nested quotes).
- Do not alter `USER_PROMPT`.
- **Important:** Run all steps in sequence without pausing once begun.

# Workflow
1. Run SlashCommand: /scout "[USER_PROMPT]" "4" -> "relevant_files_collection_path"
2. Run SlashCommand: /plan_w_docs "[USER_PROMPT]" "[DOCUMENTATION_URLS]" "[relevant_files_collection_path]" -> "path_to_plan"
3. Run SlashCommand: /build "[path_to_plan]" -> "build_report"
4. Report results per the Report section.

# Report
- Summarize files discovered (count, paths, line ranges)
- Summarize plan path + core sections
- Summarize build changes + diff stats
