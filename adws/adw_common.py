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

def generate_run_id(task_type: str, task_name: str = "") -> str:
    """Generate unique run ID in format MMDD-slug-hash."""
    import secrets
    from datetime import datetime

    date_part = datetime.now().strftime("%m%d")
    slug_part = slugify(task_type)[:20]
    if task_name:
        slug_part = f"{slug_part}-{slugify(task_name)[:10]}"
    hash_part = secrets.token_hex(2)  # 4 chars
    return f"{date_part}-{slug_part}-{hash_part}"

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


# ============================================================================
# Session & Provenance Tracking
# ============================================================================

def get_current_session() -> Dict[str, str]:
    """
    Get current Claude session info from .current_session file.
    Written by user_prompt_submit hook on every user message.

    Returns dict with:
        - session_id: Full UUID
        - short_id: First 8 chars of UUID
        - git_hash: Current git commit (short)
        - git_branch: Current git branch
        - timestamp: When session file was last updated
    """
    session_file = ROOT / '.current_session'
    if session_file.exists():
        try:
            return json.loads(session_file.read_text())
        except (json.JSONDecodeError, ValueError):
            pass

    # Fallback: try to get git info directly
    git_hash = "unknown"
    git_branch = "unknown"
    try:
        p = sh(["git", "rev-parse", "--short", "HEAD"])
        if p.returncode == 0:
            git_hash = p.stdout.strip()
        p = sh(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        if p.returncode == 0:
            git_branch = p.stdout.strip()
    except Exception:
        pass

    return {
        'session_id': 'unknown',
        'short_id': 'unknown',
        'git_hash': git_hash,
        'git_branch': git_branch,
        'timestamp': 'unknown'
    }


def get_provenance_block(format: str = "yaml") -> str:
    """
    Generate a provenance block for inclusion in outputs.

    Args:
        format: "yaml" for YAML block, "markdown" for MD header

    Returns:
        Formatted provenance string
    """
    from datetime import datetime
    session = get_current_session()

    if format == "yaml":
        return f"""# Provenance
session_id: {session['session_id']}
session_short: {session['short_id']}
git_hash: {session['git_hash']}
git_branch: {session['git_branch']}
created_at: {datetime.now().isoformat()}
"""
    elif format == "markdown":
        return f"""**Session:** `{session['short_id']}` | **Git:** `{session['git_hash']}` (`{session['git_branch']}`)
**Full Session ID:** `{session['session_id']}`
"""
    else:
        # JSON format
        return json.dumps({
            "session_id": session['session_id'],
            "session_short": session['short_id'],
            "git_hash": session['git_hash'],
            "git_branch": session['git_branch'],
            "created_at": datetime.now().isoformat()
        }, indent=2)


def generate_handoff_filename(prefix: str = "handoff") -> str:
    """
    Generate handoff filename using session short ID.
    Format: MMDD-{prefix}-{session_short}.md

    Example: 1123-handoff-f67ada19.md
    """
    from datetime import datetime
    session = get_current_session()
    date_part = datetime.now().strftime("%m%d")
    return f"{date_part}-{slugify(prefix)}-{session['short_id']}.md"
