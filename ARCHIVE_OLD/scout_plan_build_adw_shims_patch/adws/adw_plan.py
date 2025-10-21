#!/usr/bin/env python3
"""
adw_plan.py — Generate an implementation spec from USER_PROMPT + docs + scout set.
This shim focuses on file output & naming; use Claude Code to enrich content.
"""
from __future__ import annotations
import argparse, json, os
from pathlib import Path
from adws.adw_common import ensure_dir, slugify

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True, help="User prompt")
    ap.add_argument("--docs", default="", help="Comma- or space-delimited doc URLs/paths")
    ap.add_argument("--relevant", default="", help="Path to relevant_files.json from /scout")
    ap.add_argument("--outdir", default="specs", help="Output directory for the plan markdown")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    ensure_dir(outdir)

    title_slug = slugify(args.prompt)[:80] or "plan"
    plan_path = outdir / f"{title_slug}.md"

    doc_list = [d for d in (args.docs.replace(",", " ").split()) if d.strip()]
    relevant_path = Path(args.relevant) if args.relevant else None
    relevant_info = ""
    if relevant_path and relevant_path.exists():
        relevant_info = relevant_path.read_text(encoding="utf-8")

    md = f"""# {args.prompt}

## Summary
(Write a clear summary of the requested change and desired outcome.)

## Inputs
- Prompt: `{args.prompt}`
- Docs: {", ".join(doc_list) if doc_list else "(none provided)"}
- Relevant Files (from scout): 
```
{relevant_info}
```

## Architecture / Approach
- High-level design
- Data/control flow
- Affected modules and files

## Implementation Steps
1. Step-by-step edits
2. Edge cases
3. Telemetry/logging

## Tests
- Unit tests
- E2E scenarios

## Risks & Rollback
- What could go wrong
- Rollback plan

## Done Criteria
- Observable outcomes
- Diff/PR checklist
"""
    plan_path.write_text(md, encoding="utf-8")
    print(str(plan_path))

if __name__ == "__main__":
    main()
