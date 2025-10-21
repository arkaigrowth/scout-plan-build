"""Memory hooks for ADW workflow integration with mem0.

Provides cross-session learning and pattern recognition through
non-blocking memory operations that enhance workflow efficiency
without disrupting existing behavior.

Architecture:
    - Pre-execution hooks: Recall relevant patterns from memory
    - Post-execution hooks: Learn from execution results
    - Error hooks: Learn from failure patterns
    - All hooks are non-blocking (never crash workflow)

Usage:
    from adw_modules.memory_hooks import pre_scout_recall, post_scout_learn

    # Before scout
    hints = pre_scout_recall(task_description="add auth", project_id="project_scout_mvp")

    # After scout
    post_scout_learn(task_description="add auth", scout_results={...}, ...)
"""

import logging
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from adw_modules.memory_manager import MemoryManager

logger = logging.getLogger(__name__)


# ============================================================================
# Content Sanitization
# ============================================================================

def sanitize_memory_content(content: str) -> str:
    """Remove sensitive patterns before storing in memory.

    Args:
        content: Raw content that may contain secrets

    Returns:
        Sanitized content with sensitive data redacted

    Examples:
        >>> sanitize_memory_content("api_key='sk-1234'")
        "api_key='REDACTED'"
    """
    if not content:
        return content

    # Redact API keys
    content = re.sub(
        r'api_key["\']?\s*[:=]\s*["\']?[\w-]+',
        'api_key=REDACTED',
        content,
        flags=re.IGNORECASE
    )

    # Redact tokens
    content = re.sub(
        r'token["\']?\s*[:=]\s*["\']?[\w-]+',
        'token=REDACTED',
        content,
        flags=re.IGNORECASE
    )

    # Redact passwords
    content = re.sub(
        r'password["\']?\s*[:=]\s*["\']?\S+',
        'password=REDACTED',
        content,
        flags=re.IGNORECASE
    )

    # Redact email addresses
    content = re.sub(
        r'\b[\w.-]+@[\w.-]+\.\w+\b',
        'EMAIL_REDACTED',
        content
    )

    # Redact bearer tokens
    content = re.sub(
        r'Bearer\s+[\w-]+',
        'Bearer REDACTED',
        content,
        flags=re.IGNORECASE
    )

    return content


# ============================================================================
# Project ID Helpers
# ============================================================================

def get_project_id() -> str:
    """Get project-specific memory scope from git repo.

    Returns:
        Project ID in format "project_{repo_name}"

    Example:
        "project_scout_mvp" for scout_plan_build_mvp repo
    """
    try:
        from adw_modules.github import get_repo_url

        repo_url = get_repo_url()
        # Extract repo name: "github.com/owner/repo" -> "project_repo"
        repo_name = repo_url.split("/")[-1].replace(".git", "")
        return f"project_{repo_name}"
    except Exception as e:
        logger.warning(f"Failed to get project ID from git: {e}")
        return "project_default"


# ============================================================================
# Scout Phase Hooks
# ============================================================================

def pre_scout_recall(
    task_description: str,
    project_id: Optional[str] = None,
    limit: int = 10,
    threshold: float = 0.7
) -> Dict[str, Any]:
    """Recall file patterns from past similar tasks.

    Args:
        task_description: Current task (e.g., "add JWT authentication")
        project_id: Project scope (auto-detected if None)
        limit: Max memories to retrieve
        threshold: Minimum relevance score (0.0-1.0)

    Returns:
        {
            "suggested_files": ["path/to/file.py", ...],
            "key_insights": "Summary of relevant patterns",
            "confidence": 0.85,
            "memories": [{"id": "mem_123", "memory": "...", "score": 0.9}, ...]
        }

    Note:
        Never raises exceptions - returns empty results on failure
    """
    try:
        memory = MemoryManager.get_instance()

        if not memory.is_available():
            logger.debug("Memory not available, skipping recall")
            return {
                "suggested_files": [],
                "key_insights": "Memory system unavailable",
                "confidence": 0.0,
                "memories": []
            }

        project_id = project_id or get_project_id()

        # Search for similar tasks
        results = memory.search(
            query=task_description,
            user_id=project_id,
            agent_id="adw_scout",
            filters={"category": "file_patterns"},
            limit=limit,
            threshold=threshold
        )

        if not results or not results.get("results"):
            return {
                "suggested_files": [],
                "key_insights": "No prior patterns found",
                "confidence": 0.0,
                "memories": []
            }

        # Extract files from metadata
        suggested_files = []
        for mem in results["results"]:
            metadata = mem.get("metadata", {})
            if "files" in metadata:
                suggested_files.extend(metadata["files"])
            elif "file" in metadata:
                suggested_files.append(metadata["file"])

        # Deduplicate and sort by frequency
        file_counts = {}
        for f in suggested_files:
            file_counts[f] = file_counts.get(f, 0) + 1

        sorted_files = sorted(
            file_counts.keys(),
            key=lambda x: file_counts[x],
            reverse=True
        )

        # Generate insights summary
        top_memory = results["results"][0]
        key_insights = top_memory.get("memory", "")[:200]  # Truncate
        avg_confidence = sum(
            m.get("score", 0) for m in results["results"]
        ) / len(results["results"])

        logger.info(
            f"Memory recall: task='{task_description[:50]}...', "
            f"confidence={avg_confidence:.2f}, "
            f"results={len(results['results'])}"
        )

        return {
            "suggested_files": sorted_files[:limit],
            "key_insights": key_insights,
            "confidence": avg_confidence,
            "memories": results["results"]
        }

    except Exception as e:
        logger.error(f"Memory recall failed (non-blocking): {e}", exc_info=True)
        return {
            "suggested_files": [],
            "key_insights": f"Recall error: {str(e)}",
            "confidence": 0.0,
            "memories": []
        }


def post_scout_learn(
    task_description: str,
    scout_results: Dict[str, Any],
    project_id: Optional[str] = None,
    adw_id: Optional[str] = None
) -> None:
    """Learn file patterns from scout results.

    Args:
        task_description: Original task
        scout_results: Scout output (file list + key_findings)
        project_id: Project scope (auto-detected if None)
        adw_id: Session ID
    """
    try:
        memory = MemoryManager.get_instance()

        if not memory.is_available():
            logger.debug("Memory not available, skipping learning")
            return

        project_id = project_id or get_project_id()

        # Extract files from scout results
        files = []
        if "files" in scout_results:
            files = [f["path"] for f in scout_results["files"] if "path" in f]

        if not files:
            logger.debug("No files to learn from scout results")
            return  # Nothing to learn

        # Create memory message
        message = (
            f"Task '{task_description}' involved these files: "
            f"{', '.join(files[:10])}"  # Limit to top 10 files
        )

        if "key_findings" in scout_results:
            findings = scout_results["key_findings"]
            if isinstance(findings, dict) and "summary" in findings:
                message += f". Key insight: {findings['summary']}"

        # Sanitize before storing
        message = sanitize_memory_content(message)

        # Store memory
        memory.add(
            messages=message,
            user_id=project_id,
            agent_id="adw_scout",
            run_id=adw_id,
            metadata={
                "category": "file_patterns",
                "workflow": "adw_scout",
                "files": files[:20],  # Limit metadata size
                "confidence": 0.8,  # Moderate confidence (scout heuristic)
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "source": "scout_results"
            }
        )

        logger.info(
            f"Memory learn: category=file_patterns, "
            f"files={len(files)}, "
            f"adw_id={adw_id}"
        )

    except Exception as e:
        logger.error(f"Memory learning failed (non-blocking): {e}", exc_info=True)


# ============================================================================
# Plan Phase Hooks
# ============================================================================

def pre_plan_recall(
    task_description: str,
    issue_type: str,  # "feature" | "bug" | "chore"
    project_id: Optional[str] = None,
    limit: int = 5,
    threshold: float = 0.7
) -> Dict[str, Any]:
    """Recall design patterns from past planning sessions.

    Args:
        task_description: Current task description
        issue_type: Type of issue (feature/bug/chore)
        project_id: Project scope (auto-detected if None)
        limit: Max memories to retrieve
        threshold: Minimum relevance score

    Returns:
        {
            "design_patterns": ["Use Pydantic for validation", ...],
            "architecture_recommendations": "...",
            "confidence": 0.75,
            "memories": [...]
        }
    """
    try:
        memory = MemoryManager.get_instance()

        if not memory.is_available():
            return {
                "design_patterns": [],
                "architecture_recommendations": "Memory system unavailable",
                "confidence": 0.0,
                "memories": []
            }

        project_id = project_id or get_project_id()

        # Search for similar plans
        results = memory.search(
            query=task_description,
            user_id=project_id,
            agent_id="adw_plan",
            filters={"category": "design_decisions", "issue_type": issue_type},
            limit=limit,
            threshold=threshold
        )

        if not results or not results.get("results"):
            return {
                "design_patterns": [],
                "architecture_recommendations": "No prior patterns found",
                "confidence": 0.0,
                "memories": []
            }

        # Extract patterns
        patterns = [mem.get("memory", "") for mem in results["results"]]

        # Aggregate into recommendations
        recommendations = "\n".join([
            f"- {pattern[:150]}" for pattern in patterns[:3]
        ])

        avg_confidence = sum(
            m.get("score", 0) for m in results["results"]
        ) / len(results["results"])

        logger.info(
            f"Memory recall: task='{task_description[:50]}...', "
            f"type={issue_type}, "
            f"confidence={avg_confidence:.2f}"
        )

        return {
            "design_patterns": patterns,
            "architecture_recommendations": recommendations,
            "confidence": avg_confidence,
            "memories": results["results"]
        }

    except Exception as e:
        logger.error(f"Memory recall failed (non-blocking): {e}", exc_info=True)
        return {
            "design_patterns": [],
            "architecture_recommendations": f"Recall error: {str(e)}",
            "confidence": 0.0,
            "memories": []
        }


def post_plan_learn(
    plan_file: str,
    project_id: Optional[str] = None,
    adw_id: Optional[str] = None,
    issue_type: Optional[str] = None
) -> None:
    """Extract design decisions from plan markdown.

    Parses plan sections like:
    - Architecture/Approach
    - Risks and Mitigation
    - Implementation Steps

    And stores key decisions as memories.

    Args:
        plan_file: Path to plan markdown file
        project_id: Project scope (auto-detected if None)
        adw_id: Session ID
        issue_type: Type of issue (feature/bug/chore)
    """
    try:
        memory = MemoryManager.get_instance()

        if not memory.is_available():
            logger.debug("Memory not available, skipping learning")
            return

        project_id = project_id or get_project_id()

        # Read plan file
        with open(plan_file, "r") as f:
            plan_content = f.read()

        # Extract sections (simplified - could use markdown parser)
        sections = {
            "architecture": _extract_section(plan_content, "Architecture"),
            "risks": _extract_section(plan_content, "Risks"),
            "implementation": _extract_section(plan_content, "Implementation")
        }

        # Store architecture decisions
        if sections["architecture"]:
            arch_message = f"Architecture decision: {sections['architecture'][:500]}"
            arch_message = sanitize_memory_content(arch_message)

            memory.add(
                messages=arch_message,
                user_id=project_id,
                agent_id="adw_plan",
                run_id=adw_id,
                metadata={
                    "category": "design_decisions",
                    "workflow": "adw_plan",
                    "issue_type": issue_type,
                    "confidence": 0.9,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "source": "plan_analysis"
                }
            )

        # Store risk patterns
        if sections["risks"]:
            risk_message = f"Risk mitigation: {sections['risks'][:500]}"
            risk_message = sanitize_memory_content(risk_message)

            memory.add(
                messages=risk_message,
                user_id=project_id,
                agent_id="adw_plan",
                run_id=adw_id,
                metadata={
                    "category": "design_decisions",
                    "workflow": "adw_plan",
                    "tags": ["risk", "mitigation"],
                    "confidence": 0.85,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "source": "plan_analysis"
                }
            )

        logger.info(
            f"Memory learn: category=design_decisions, "
            f"plan_file={plan_file}, "
            f"adw_id={adw_id}"
        )

    except Exception as e:
        logger.error(f"Memory learning failed (non-blocking): {e}", exc_info=True)


def _extract_section(content: str, section_name: str) -> str:
    """Extract content from markdown section.

    Args:
        content: Full markdown content
        section_name: Section header to find (e.g., "Architecture")

    Returns:
        Section content or empty string if not found
    """
    # Look for section header (# or ##)
    pattern = rf"#{1,3}\s+{section_name}[^\n]*\n(.*?)(?=\n#{1,3}\s+|\Z)"
    match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)

    if match:
        return match.group(1).strip()
    return ""


# ============================================================================
# Build Phase Hooks
# ============================================================================

def post_build_learn(
    build_report_file: str,
    project_id: Optional[str] = None,
    adw_id: Optional[str] = None
) -> None:
    """Extract implementation patterns from build report.

    Build reports contain:
    - Files changed
    - Libraries used
    - Implementation decisions
    - Test results

    Args:
        build_report_file: Path to build report markdown
        project_id: Project scope (auto-detected if None)
        adw_id: Session ID
    """
    try:
        memory = MemoryManager.get_instance()

        if not memory.is_available():
            logger.debug("Memory not available, skipping learning")
            return

        project_id = project_id or get_project_id()

        # Read build report
        with open(build_report_file, "r") as f:
            report_content = f.read()

        # Parse report (simplified - could use structured format)
        files_changed = _extract_files_changed(report_content)
        libraries_used = _extract_libraries(report_content)

        # Store implementation pattern
        if libraries_used:
            message = f"Implementation used libraries: {', '.join(libraries_used)}"
            message = sanitize_memory_content(message)

            memory.add(
                messages=message,
                user_id=project_id,
                agent_id="adw_build",
                run_id=adw_id,
                metadata={
                    "category": "implementation_patterns",
                    "workflow": "adw_build",
                    "files": files_changed,
                    "tags": libraries_used,
                    "confidence": 0.9,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "source": "build_report"
                }
            )

            logger.info(
                f"Memory learn: category=implementation_patterns, "
                f"libraries={len(libraries_used)}, "
                f"adw_id={adw_id}"
            )

    except Exception as e:
        logger.error(f"Memory learning failed (non-blocking): {e}", exc_info=True)


def _extract_files_changed(report_content: str) -> List[str]:
    """Extract list of files changed from build report.

    Args:
        report_content: Build report markdown

    Returns:
        List of file paths
    """
    files = []
    # Look for common patterns: "Modified: path/to/file.py"
    pattern = r"(?:Modified|Created|Updated):\s*([^\s]+\.(?:py|js|ts|md))"
    matches = re.findall(pattern, report_content, re.MULTILINE)
    files.extend(matches)
    return list(set(files))  # Deduplicate


def _extract_libraries(report_content: str) -> List[str]:
    """Extract library names from build report.

    Args:
        report_content: Build report markdown

    Returns:
        List of library names
    """
    libraries = []
    # Look for import/require statements mentioned in report
    patterns = [
        r"import\s+(\w+)",
        r"from\s+(\w+)\s+import",
        r"require\(['\"](\w+)['\"]\)"
    ]

    for pattern in patterns:
        matches = re.findall(pattern, report_content)
        libraries.extend(matches)

    # Filter out common builtins
    builtins = {"os", "sys", "re", "json", "time", "datetime"}
    libraries = [lib for lib in libraries if lib not in builtins]

    return list(set(libraries))  # Deduplicate


# ============================================================================
# Error Learning Hook
# ============================================================================

def on_error_learn(
    error: Exception,
    context: Dict[str, Any],
    resolution: Optional[str] = None,
    project_id: Optional[str] = None
) -> None:
    """Learn from errors for future prevention.

    Args:
        error: Exception that occurred
        context: Error context (workflow, file, etc.)
        resolution: How it was fixed (if known)
        project_id: Project scope (auto-detected if None)
    """
    try:
        memory = MemoryManager.get_instance()

        if not memory.is_available():
            logger.debug("Memory not available, skipping error learning")
            return

        project_id = project_id or get_project_id()

        error_type = type(error).__name__
        error_message = str(error)

        # Build memory message
        message = f"Error: {error_type}: {error_message}"
        if resolution:
            message += f". Solution: {resolution}"

        # Sanitize error message (may contain sensitive data)
        message = sanitize_memory_content(message)

        # Extract workflow from context
        workflow = context.get("workflow", "unknown")

        memory.add(
            messages=message,
            user_id=project_id,
            agent_id=f"adw_{workflow}",
            metadata={
                "category": "error_resolutions",
                "workflow": f"adw_{workflow}",
                "tags": [error_type.lower(), "error"],
                "confidence": 1.0 if resolution else 0.5,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "source": "error_handler",
                **context  # Include file, adw_id, etc.
            }
        )

        logger.info(
            f"Memory learn: category=error_resolutions, "
            f"error={error_type}, "
            f"workflow={workflow}"
        )

    except Exception as e:
        logger.error(f"Error learning failed (non-blocking): {e}", exc_info=True)


# ============================================================================
# Memory Cleanup Utilities
# ============================================================================

def cleanup_old_memories(
    project_id: Optional[str] = None,
    max_age_days: int = 365
) -> int:
    """Delete memories older than retention period.

    Args:
        project_id: Project scope (auto-detected if None)
        max_age_days: Maximum age in days (default: 365)

    Returns:
        Number of memories deleted
    """
    try:
        memory = MemoryManager.get_instance()

        if not memory.is_available():
            logger.warning("Memory not available, skipping cleanup")
            return 0

        project_id = project_id or get_project_id()

        cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)

        # Get all memories for project
        all_memories = memory.get_all(user_id=project_id, limit=1000)

        if not all_memories or not all_memories.get("results"):
            return 0

        deleted_count = 0
        for mem in all_memories["results"]:
            timestamp_str = mem.get("metadata", {}).get("timestamp")
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace("Z", ""))
                    if timestamp < cutoff_date:
                        memory.delete(mem["id"])
                        deleted_count += 1
                except ValueError:
                    # Invalid timestamp, skip
                    continue

        logger.info(f"Cleaned up {deleted_count} old memories (>{max_age_days} days)")
        return deleted_count

    except Exception as e:
        logger.error(f"Memory cleanup failed: {e}", exc_info=True)
        return 0
