# ADW Workflow Extraction

Extract ADW workflow information from the text below and return a JSON response.

## Instructions

- Look for ADW workflow commands in the text (e.g., `/adw_plan`, `/adw_build`, `/adw_test`, `/adw_review`, `/adw_document`, `/adw_patch`, `/adw_plan_build`, `/adw_plan_build_test`, `/adw_plan_build_test_review`, `/adw_sdlc`)
- Look for ADW IDs (8-character alphanumeric strings, often after "adw_id:" or "ADW ID:" or similar)
- Return a JSON object with the extracted information
- If no ADW workflow is found, return empty JSON: `{}`

## Valid ADW Commands

- `/adw_plan` - Planning only
- `/adw_build` - Building only (requires adw_id)
- `/adw_test` - Testing only (requires adw_id)
- `/adw_review` - Review only (requires adw_id)
- `/adw_document` - Documentation only (requires adw_id)
- `/adw_patch` - Direct patch from issue
- `/adw_plan_build` - Plan + Build
- `/adw_plan_build_test` - Plan + Build + Test
- `/adw_plan_build_review` - Plan + Build + Review (skips test)
- `/adw_plan_build_document` - Plan + Build + Document (skips test and review)
- `/adw_plan_build_test_review` - Plan + Build + Test + Review
- `/adw_sdlc` - Complete SDLC: Plan + Build + Test + Review + Document

## Response Format

Respond ONLY with a JSON object in this format:
```json
{
  "adw_slash_command": "/adw_plan",
  "adw_id": "abc12345"
}
```

Fields:
- `adw_slash_command`: The ADW command found (include the slash)
- `adw_id`: The 8-character ADW ID if found

If only one field is found, include only that field.
If nothing is found, return: `{}`

## Text to Analyze

$ARGUMENTS