#!/usr/bin/env python3
"""
adw_review.py — Minimal review shim
- Summarize diff, plan, and emit a markdown review.
- (Optional) If GH env present, you can extend to post review comments via gh CLI.
"""
from __future__ import annotations
import argparse, os, json
from pathlib import Path
from adws.adw_common import PlanDoc, git_diff_stat, ensure_dir

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan_path")
    ap.add_argument("--outdir", default="ai_docs/reviews")
    args = ap.parse_args()

    plan = PlanDoc.load(Path(args.plan_path))
    ensure_dir(Path(args.outdir))

    diff = git_diff_stat()
    md = f"""# Review

**Plan:** {plan.path}

## Summary of Plan
Sections: {", ".join(plan.sections.keys())}

## Diff Overview
```
{diff}
```

## Reviewer Notes
- LGTM with nits (example)
- Consider adding more tests for edge cases
"""
    out = Path(args.outdir) / (plan.path.stem + "-review.md")
    out.write_text(md, encoding="utf-8")
    print(str(out))

if __name__ == "__main__":
    main()
