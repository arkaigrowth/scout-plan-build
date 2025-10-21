#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///

import os
from pathlib import Path

LOG_BASE_DIR = os.environ.get("CLAUDE_HOOKS_LOG_DIR", "logs")

def get_session_log_dir(session_id: str) -> Path:
    return Path(LOG_BASE_DIR) / session_id

def ensure_session_log_dir(session_id: str) -> Path:
    log_dir = get_session_log_dir(session_id)
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir
