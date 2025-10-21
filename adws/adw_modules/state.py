"""State management for ADW composable architecture.

Provides persistent state management via file storage and
transient state passing between scripts via stdin/stdout.
"""

import json
import os
import sys
import logging
from typing import Dict, Any, Optional
from adw_modules.data_types import ADWStateData
from adw_modules.exceptions import StateError, ValidationError, FileSystemError


class ADWState:
    """Container for ADW workflow state with file persistence."""

    STATE_FILENAME = "adw_state.json"

    def __init__(self, adw_id: str):
        """Initialize ADWState with a required ADW ID.

        Args:
            adw_id: The ADW ID for this state (required)

        Raises:
            ValidationError: If adw_id is invalid
        """
        if not adw_id:
            raise ValidationError(
                "adw_id is required for ADWState",
                field="adw_id"
            )
        if not isinstance(adw_id, str) or len(adw_id) < 1:
            raise ValidationError(
                "adw_id must be a non-empty string",
                field="adw_id",
                actual_value=adw_id
            )

        self.adw_id = adw_id
        # Start with minimal state
        self.data: Dict[str, Any] = {"adw_id": self.adw_id}
        self.logger = logging.getLogger(__name__)

    def update(self, **kwargs):
        """Update state with new key-value pairs."""
        # Filter to only our core fields
        core_fields = {"adw_id", "issue_number", "branch_name", "plan_file", "issue_class"}
        for key, value in kwargs.items():
            if key in core_fields:
                self.data[key] = value

    def get(self, key: str, default=None):
        """Get value from state by key."""
        return self.data.get(key, default)

    def get_state_path(self) -> str:
        """Get path to state file."""
        project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        return os.path.join(project_root, "agents", self.adw_id, self.STATE_FILENAME)

    def save(self, workflow_step: Optional[str] = None) -> None:
        """Save state to file in agents/{adw_id}/adw_state.json.

        Raises:
            StateError: If state validation fails
            FileSystemError: If file write fails
        """
        state_path = self.get_state_path()

        try:
            os.makedirs(os.path.dirname(state_path), exist_ok=True)
        except OSError as e:
            raise FileSystemError(
                f"Failed to create state directory",
                path=os.path.dirname(state_path),
                operation="mkdir",
                error=str(e)
            ) from e

        # Create ADWStateData for validation
        try:
            state_data = ADWStateData(
                adw_id=self.data.get("adw_id"),
                issue_number=self.data.get("issue_number"),
                branch_name=self.data.get("branch_name"),
                plan_file=self.data.get("plan_file"),
                issue_class=self.data.get("issue_class"),
            )
        except Exception as e:
            raise StateError(
                "State validation failed during save",
                adw_id=self.adw_id,
                validation_error=str(e),
                state_data=self.data
            ) from e

        # Save as JSON
        try:
            with open(state_path, "w") as f:
                json.dump(state_data.model_dump(), f, indent=2)
        except (OSError, IOError) as e:
            raise FileSystemError(
                f"Failed to write state file",
                path=state_path,
                operation="write",
                error=str(e)
            ) from e

        self.logger.info(f"Saved state to {state_path}")
        if workflow_step:
            self.logger.info(f"State updated by: {workflow_step}")

    @classmethod
    def load(
        cls, adw_id: str, logger: Optional[logging.Logger] = None
    ) -> Optional["ADWState"]:
        """Load state from file if it exists.

        Returns:
            ADWState instance if found and valid, None otherwise

        Note:
            Does not raise exceptions - returns None on any error for compatibility
        """
        project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        state_path = os.path.join(project_root, "agents", adw_id, cls.STATE_FILENAME)

        if not os.path.exists(state_path):
            return None

        try:
            with open(state_path, "r") as f:
                data = json.load(f)

            # Validate with ADWStateData
            state_data = ADWStateData(**data)

            # Create ADWState instance
            state = cls(state_data.adw_id)
            state.data = state_data.model_dump()

            if logger:
                logger.info(f"🔍 Found existing state from {state_path}")
                logger.info(f"State: {json.dumps(state_data.model_dump(), indent=2)}")

            return state
        except ValidationError as e:
            if logger:
                logger.error(f"State validation failed for {state_path}: {e.message}")
            return None
        except (FileSystemError, json.JSONDecodeError) as e:
            if logger:
                logger.error(f"Failed to load state from {state_path}: {str(e)}")
            return None
        except Exception as e:
            if logger:
                logger.error(f"Unexpected error loading state from {state_path}: {e}")
            return None

    @classmethod
    def from_stdin(cls) -> Optional["ADWState"]:
        """Read state from stdin if available (for piped input).

        Returns:
            ADWState instance if valid input found, None otherwise

        Note:
            Does not raise exceptions - returns None on any error for compatibility
        """
        if sys.stdin.isatty():
            return None
        try:
            input_data = sys.stdin.read()
            if not input_data.strip():
                return None
            data = json.loads(input_data)
            adw_id = data.get("adw_id")
            if not adw_id:
                return None  # No valid state without adw_id
            state = cls(adw_id)
            state.data = data
            return state
        except (json.JSONDecodeError, EOFError, ValidationError):
            return None
        except Exception:
            return None

    def to_stdout(self):
        """Write state to stdout as JSON (for piping to next script)."""
        # Only output core fields
        output_data = {
            "adw_id": self.data.get("adw_id"),
            "issue_number": self.data.get("issue_number"),
            "branch_name": self.data.get("branch_name"),
            "plan_file": self.data.get("plan_file"),
            "issue_class": self.data.get("issue_class"),
        }
        print(json.dumps(output_data, indent=2))
