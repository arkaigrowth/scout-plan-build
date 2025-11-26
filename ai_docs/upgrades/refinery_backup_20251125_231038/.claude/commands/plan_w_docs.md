# Quick Plan (with Docs)

# Purpose
Create a detailed implementation plan based on the `USER_PROMPT`, pulling in documentation and scouted file ranges. Save to `specs/<kebab-title>.md`.

# Variables
USER_PROMPT: $1
DOCUMENTATION_URLS: $2
RELEVANT_FILES_COLLECTION: $3
PLAN_OUTPUT_DIRECTORY: "specs/"
DOCUMENTATION_OUTPUT_DIRECTORY: "ai_docs/"

# Workflow
1) Analyze Requirements — parse the request; define deliverables and acceptance criteria.
2) Scrape Docs — for each DOC URL: use `firecrawl` or `webfetch` via Task->Bash; save excerpts into `ai_docs/`.
3) Design Solution — outline architecture, data flow, file edits, test strategy.
4) Document Plan — write a thorough spec (problem, approach, implementation steps, testing, risks).
5) Filename — derive `<kebab-title>.md`.
6) Save & Report — write under `specs/` and return the path.
