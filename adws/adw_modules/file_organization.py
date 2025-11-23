#!/usr/bin/env python3
"""
File Organization Module - Standardized output management for ADW workflows

This module addresses the scattered output problem by providing:
1. Timestamped output directories
2. Consistent naming conventions
3. Automatic cleanup of old outputs
4. Task context preservation
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

class FileOrganizer:
    """Manages standardized file output for ADW workflows."""

    def __init__(self, base_dir: str = "ai_docs/outputs"):
        """Initialize with base output directory."""
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

        # Legacy directories for compatibility
        self.legacy_dirs = {
            "scout": Path("scout_outputs"),
            "specs": Path("specs"),
            "build_reports": Path("ai_docs/build_reports"),
            "reviews": Path("ai_docs/reviews")
        }

        # Ensure legacy dirs exist
        for dir_path in self.legacy_dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)

    def create_task_directory(self,
                            task_name: str,
                            adw_id: Optional[str] = None) -> Path:
        """
        Create a timestamped directory for a specific task.

        Args:
            task_name: Name/description of the task
            adw_id: Optional ADW identifier

        Returns:
            Path to the created directory
        """
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

        # Clean task name for filesystem
        clean_name = "".join(c if c.isalnum() or c in "-_" else "_"
                            for c in task_name.lower())[:50]

        # Build directory name
        if adw_id:
            dir_name = f"{timestamp}-{adw_id}-{clean_name}"
        else:
            dir_name = f"{timestamp}-{clean_name}"

        # Create directory
        task_dir = self.base_dir / dir_name
        task_dir.mkdir(parents=True, exist_ok=True)

        # Create metadata file
        metadata = {
            "created": datetime.now().isoformat(),
            "task": task_name,
            "adw_id": adw_id,
            "timestamp": timestamp,
            "directory": str(task_dir)
        }

        with open(task_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        # Update latest symlink
        self._update_latest_link(task_dir)

        return task_dir

    def save_scout_output(self,
                         data: Dict[str, Any],
                         task_dir: Optional[Path] = None,
                         also_legacy: bool = True) -> Path:
        """
        Save scout output with proper organization.

        Args:
            data: Scout results data
            task_dir: Optional task directory (creates new if not provided)
            also_legacy: Also save to legacy location for compatibility

        Returns:
            Path to saved file
        """
        if task_dir is None:
            task_dir = self.create_task_directory("scout-operation")

        # Save to task directory
        output_file = task_dir / "scout.json"
        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)

        # Also save to legacy location for compatibility
        if also_legacy:
            legacy_file = self.legacy_dirs["scout"] / "relevant_files.json"
            with open(legacy_file, "w") as f:
                json.dump(data, f, indent=2)

        return output_file

    def save_plan_output(self,
                        content: str,
                        issue_num: str,
                        adw_id: str,
                        slug: str,
                        task_dir: Optional[Path] = None) -> Path:
        """
        Save plan/spec output with proper naming.

        Args:
            content: Plan markdown content
            issue_num: Issue number
            adw_id: ADW identifier
            slug: URL-friendly slug
            task_dir: Optional task directory

        Returns:
            Path to saved file
        """
        # Standard spec filename
        filename = f"issue-{issue_num}-adw-{adw_id}-{slug}.md"

        # Save to specs directory (primary location)
        spec_file = self.legacy_dirs["specs"] / filename
        with open(spec_file, "w") as f:
            f.write(content)

        # Also save to task directory if provided
        if task_dir:
            task_file = task_dir / "plan.md"
            with open(task_file, "w") as f:
                f.write(content)

        return spec_file

    def save_build_output(self,
                         content: str,
                         slug: str,
                         task_dir: Optional[Path] = None) -> Path:
        """
        Save build report with proper organization.

        Args:
            content: Build report content
            slug: URL-friendly slug
            task_dir: Optional task directory

        Returns:
            Path to saved file
        """
        # Save to legacy location
        filename = f"{slug}-build-report.md"
        legacy_file = self.legacy_dirs["build_reports"] / filename
        with open(legacy_file, "w") as f:
            f.write(content)

        # Also save to task directory if provided
        if task_dir:
            task_file = task_dir / "build-report.md"
            with open(task_file, "w") as f:
                f.write(content)

        return legacy_file

    def cleanup_old_outputs(self, days: int = 7, dry_run: bool = True):
        """
        Clean up old output directories.

        Args:
            days: Remove directories older than this many days
            dry_run: If True, only show what would be deleted
        """
        cutoff = datetime.now().timestamp() - (days * 86400)

        for task_dir in self.base_dir.iterdir():
            if not task_dir.is_dir():
                continue

            # Skip latest symlink
            if task_dir.name == "latest":
                continue

            # Check age
            if task_dir.stat().st_mtime < cutoff:
                if dry_run:
                    print(f"Would remove: {task_dir}")
                else:
                    print(f"Removing: {task_dir}")
                    shutil.rmtree(task_dir)

    def _update_latest_link(self, target_dir: Path):
        """Update the 'latest' symlink to point to the most recent directory."""
        latest_link = self.base_dir / "latest"

        # Remove existing symlink if present
        if latest_link.exists() or latest_link.is_symlink():
            latest_link.unlink()

        # Create new symlink (relative path for portability)
        try:
            relative_target = Path(os.path.relpath(target_dir, self.base_dir))
            latest_link.symlink_to(relative_target)
        except OSError:
            # Fallback for systems that don't support symlinks
            # Create a text file with the path instead
            with open(latest_link.with_suffix(".txt"), "w") as f:
                f.write(str(target_dir))

    def get_latest_directory(self) -> Optional[Path]:
        """Get the most recent task directory."""
        latest_link = self.base_dir / "latest"

        # Check symlink
        if latest_link.is_symlink():
            return latest_link.resolve()

        # Check text file fallback
        latest_txt = latest_link.with_suffix(".txt")
        if latest_txt.exists():
            with open(latest_txt) as f:
                return Path(f.read().strip())

        # Find most recent directory by timestamp
        dirs = [d for d in self.base_dir.iterdir()
                if d.is_dir() and d.name != "latest"]
        if dirs:
            return max(dirs, key=lambda d: d.stat().st_mtime)

        return None

    def consolidate_scattered_files(self, dry_run: bool = True):
        """
        Find and consolidate scattered output files.

        This helps clean up the mess of files in various locations.
        """
        patterns = [
            ("*.md", "Root markdown files"),
            ("MEOW_*.md", "MEOW loader files"),
            ("*_relevant_files.json", "Scout outputs"),
            ("*-build-report.md", "Build reports"),
            ("*-review.md", "Review files")
        ]

        consolidated_dir = self.base_dir / "consolidated"
        if not dry_run:
            consolidated_dir.mkdir(exist_ok=True)

        for pattern, description in patterns:
            print(f"\nSearching for {description} ({pattern})...")

            # Search in project root
            for file in Path(".").glob(pattern):
                # Skip expected files
                if file.name in ["README.md", "CLAUDE.md", "WHERE_ARE_THE_PLANS.md"]:
                    continue

                if dry_run:
                    print(f"  Would move: {file}")
                else:
                    dest = consolidated_dir / file.name
                    print(f"  Moving: {file} -> {dest}")
                    shutil.move(str(file), str(dest))


def setup_file_organization():
    """One-time setup to organize existing files."""
    organizer = FileOrganizer()

    print("=== File Organization Setup ===\n")

    # Check for scattered files
    print("1. Checking for scattered files...")
    organizer.consolidate_scattered_files(dry_run=True)

    response = input("\nConsolidate these files? (y/n): ")
    if response.lower() == "y":
        organizer.consolidate_scattered_files(dry_run=False)
        print("✅ Files consolidated")

    # Check for old outputs
    print("\n2. Checking for old outputs...")
    organizer.cleanup_old_outputs(days=7, dry_run=True)

    response = input("\nRemove old outputs? (y/n): ")
    if response.lower() == "y":
        organizer.cleanup_old_outputs(days=7, dry_run=False)
        print("✅ Old outputs cleaned")

    print("\n✅ File organization setup complete!")
    print(f"   Output directory: {organizer.base_dir}")
    print(f"   Latest: {organizer.get_latest_directory()}")


# Example usage in ADW workflows
def example_usage():
    """Example of how to use FileOrganizer in ADW workflows."""

    # Initialize organizer
    organizer = FileOrganizer()

    # Create task directory for a new feature
    task_dir = organizer.create_task_directory(
        task_name="jwt-authentication",
        adw_id="AUTH-001"
    )
    print(f"Created task directory: {task_dir}")

    # Save scout results
    scout_data = {"files": ["auth.py", "routes.py", "tests/test_auth.py"]}
    scout_file = organizer.save_scout_output(scout_data, task_dir)
    print(f"Saved scout results: {scout_file}")

    # Save plan
    plan_content = "# JWT Authentication Plan\n\n## Overview..."
    plan_file = organizer.save_plan_output(
        content=plan_content,
        issue_num="123",
        adw_id="AUTH-001",
        slug="jwt-auth",
        task_dir=task_dir
    )
    print(f"Saved plan: {plan_file}")

    # Save build report
    build_content = "# Build Report\n\n## Changes Made..."
    build_file = organizer.save_build_output(
        content=build_content,
        slug="jwt-auth",
        task_dir=task_dir
    )
    print(f"Saved build report: {build_file}")

    # Get latest directory
    latest = organizer.get_latest_directory()
    print(f"Latest output directory: {latest}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_file_organization()
    else:
        example_usage()