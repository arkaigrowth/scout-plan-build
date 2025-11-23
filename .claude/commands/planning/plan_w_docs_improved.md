---
allowed-tools: Read, Write, Edit, Glob, Grep, MultiEdit
description: Creates a concise engineering implementation plan based on user requirements and saves it to specs directory
argument-hint: [user-prompt] [documentation-urls] [relevant-files]
model: claude-sonnet-4-5-20250929
---

<!-- risk: mutate-local -->
<!-- auto-invoke: gated -->

# Quick Plan

Create a detailed implementation plan based on the user's requirements provided through the `USER_PROMPT` variable. Analyze the request, pull in the documentation, think through the implementation approach, and save a comprehensive specification document to `PLAN_OUTPUT_DIRECTORY/<name-of-plan>.md` that can be used as a blueprint for actual development work. Follow the `Instructions` and work through the `Workflow` to create the plan.

## Variables
USER_PROMPT: $1
DOCUMENTATION_URLS: $2
RELEVANT_FILES_COLLECTION: $3
PLAN_OUTPUT_DIRECTORY: `specs/`
DOCUMENTATION_OUTPUT_DIRECTORY: `ai_docs/`

## Instructions

- IMPORTANT: If no `USER_PROMPT`, `DOCUMENTATION_URLS`, or `RELEVANT_FILES_COLLECTION` is provided, stop and ask the user to provide them.
- READ the `RELEVANT_FILES_COLLECTION` file which contains a structured bullet point list of files with line ranges:
  - `<path to file> (offset: N, limit: M)`
- Carefully analyze the user's requirements provided in the USER_PROMPT variable
- If DOCUMENTATION_URLS are provided, research each URL to understand the APIs, patterns, and best practices
- Cross-reference the relevant files from the scout phase to understand the existing codebase structure
- Design a solution that integrates well with the existing architecture
- Create a comprehensive, actionable plan that can be directly implemented

## Workflow

1. Analyze Requirements - THINK HARD and parse the USER_PROMPT to understand the core problem and desired outcome
2. Scrape Documentation - With Task, in parallel, scrape each DOCUMENTATION_URLS with firecrawl (or webfetch if firecrawl is not available)
3. Design Solution - Develop technical approach including architecture decisions and implementation strategy
4. Document Plan - Structure a comprehensive markdown document with problem statement, implementation steps, and testing approach
5. Generate Filename - Create a descriptive kebab-case filename based on the plan's main topic
6. Save & Report - Follow the `Report` section to write the plan to `PLAN_OUTPUT_DIRECTORY/<filename>.md` and provide a summary of key components

## Report

### Plan Structure
The plan should include these sections:

```markdown
# Plan: [Title]

## Summary
Brief overview of what we're building and why

## Problem Statement
Clear articulation of the problem we're solving

## Inputs
- Scout Results: Path to relevant_files.json and key findings
- Documentation References: Key APIs and patterns discovered
- Constraints: Any limitations or requirements

## Architecture/Approach
- High-level design decisions
- Component interactions
- Data flow
- Integration points

## Implementation Steps
### Step 1: [Name]
- Detailed actions
- Files to modify/create
- Code patterns to follow

### Step 2: [Name]
...

## Testing Strategy
- Unit tests needed
- Integration tests
- Validation criteria

## Risks and Mitigation
- Potential issues
- Fallback strategies
- Rollback plan

## Success Criteria
- Measurable outcomes
- Definition of done
- Acceptance criteria
```

### Output
- Save the plan to `PLAN_OUTPUT_DIRECTORY/<kebab-case-title>.md`
- Return the full path to the saved plan file
- Provide a brief summary of the plan's key components in the response