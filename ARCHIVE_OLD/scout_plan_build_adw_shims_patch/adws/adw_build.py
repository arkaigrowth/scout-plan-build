#!/usr/bin/env python3
"""
adw_build.py — Apply changes per a plan file; produce a concise build report.
This shim does not attempt to implement code edits itself; it structures the loop:
- Load plan
- (TODO) Call sub-agents or tools to make atomic edits
- Emit diff stats + report
"""
from __future__ import annotations
import argparse, os, sys
from pathlib import Path
from adws.adw_common import PlanDoc, BuildReport, git_diff_stat, ensure_dir

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan_path", help="Path to the plan markdown file created by adw_plan.py")
    ap.add_argument("--report-dir", default="ai_docs/build_reports", help="Where to write the build report")
    args = ap.parse_args()

    plan = PlanDoc.load(Path(args.plan_path))

    steps_applied = []
    notes = []

    # (Phase 1) Validate scope
    if "Implementation Steps" not in plan.sections:
        notes.append("Plan missing 'Implementation Steps'; stopping early.")
        diff = git_diff_stat()
        report = BuildReport(plan_path=Path(args.plan_path), steps_applied=steps_applied, notes=notes, diff_stat=diff)
        outdir = Path(args.report_dir); ensure_dir(outdir)
        out = outdir / (plan.path.stem + "-build-report.md")
        out.write_text(report.to_md(), encoding="utf-8")
        print(str(out))
        sys.exit(0)

    # (Phase 2) TODO: Implement changes
    # Here you can call your editor/LLM agents, or structured tools, in small atomic steps.
    # For the MVP shim, we only record the intent.
    impl = plan.sections["Implementation Steps"]
    steps_applied.append("Parsed 'Implementation Steps' and queued edits (placeholder).")

    # (Phase 3) Diff + report
    diff = git_diff_stat()
    report = BuildReport(plan_path=Path(args.plan_path), steps_applied=steps_applied, notes=notes, diff_stat=diff)
    outdir = Path(args.report_dir); ensure_dir(outdir)
    out = outdir / (plan.path.stem + "-build-report.md")
    out.write_text(report.to_md(), encoding="utf-8")
    print(str(out))

if __name__ == "__main__":
    main()
