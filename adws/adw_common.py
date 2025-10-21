#!/usr/bin/env python3
"""
ADW common utilities: logging, git helpers, plan parsing, reporting.
Safe-by-default, no .env reads; rely on environment provided by OS.
"""
from __future__ import annotations
import json, subprocess, sys, re, os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict, Any

ROOT = Path.cwd()

def sh(cmd: List[str], cwd: Path | None = None, check: bool = False) -> subprocess.CompletedProcess:
    """Run a shell command without invoking a shell; returns CompletedProcess.
    We avoid `shell=True` for safety; commands must be passed as list tokens."""
    return subprocess.run(cmd, cwd=str(cwd or ROOT), capture_output=True, text=True, check=check)

def git_diff_stat() -> str:
    p = sh(["git", "diff", "--stat"])
    return p.stdout.strip()

def git_root() -> Path:
    p = sh(["git", "rev-parse", "--show-toplevel"])
    return Path(p.stdout.strip()) if p.returncode == 0 else ROOT

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return re.sub(r"-+", "-", text).strip("-")

@dataclass
class PlanDoc:
    title: str
    path: Path
    sections: Dict[str, str]

    @classmethod
    def load(cls, plan_path: Path) -> "PlanDoc":
        md = plan_path.read_text(encoding="utf-8")
        # very light parser: split by top-level headings
        sections: Dict[str,str] = {}
        cur = "Preamble"
        buf: List[str] = []
        for line in md.splitlines():
            if line.startswith("# "):
                if buf:
                    sections[cur] = "\n".join(buf).strip()
                    buf = []
                cur = line[2:].strip()
            else:
                buf.append(line)
        if buf:
            sections[cur] = "\n".join(buf).strip()
        title = plan_path.stem.replace("-", " ").title()
        return cls(title=title, path=plan_path, sections=sections)

@dataclass
class BuildReport:
    plan_path: Path
    steps_applied: List[str]
    notes: List[str]
    diff_stat: str

    def to_md(self) -> str:
        return (
            f"# Build Report\n\n"
            f"**Plan:** {self.plan_path}\n\n"
            f"## Steps Applied\n" + "".join(f"- {s}\n" for s in self.steps_applied) + "\n"
            f"## Notes\n" + "".join(f"- {n}\n" for n in self.notes) + "\n"
            f"## Diff Stat\n```\n{self.diff_stat}\n```\n"
        )

def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)
