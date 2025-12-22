# Installer Implementation Specification

**Target**: Implement installer that reads components-v2.yaml
**Complexity**: Moderate (hierarchical selection + dependency resolution)
**Estimated Effort**: 8 hours

## Architecture Overview

```
┌──────────────────────────────────────────────────┐
│                  CLI Interface                    │
│  install.sh --profile=standard                   │
│  install.sh --custom --select=...                │
│  install.sh --interactive                        │
└──────────────────┬───────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────┐
│          Component Resolver                       │
│  - Parse components-v2.yaml                      │
│  - Resolve dependencies                          │
│  - Validate selections                           │
└──────────────────┬───────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────┐
│          File Installer                          │
│  - Copy files in dependency order                │
│  - Create directories                            │
│  - Generate configs                              │
└──────────────────┬───────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────┐
│          Validator                               │
│  - Run profile-specific checks                   │
│  - Generate .adw_install_manifest.json           │
│  - Report installation status                    │
└──────────────────────────────────────────────────┘
```

## Core Modules

### 1. ComponentResolver (Python)

**Purpose**: Parse YAML and resolve dependencies

```python
# scripts/component_resolver.py

from dataclasses import dataclass
from typing import List, Dict, Set
import yaml

@dataclass
class Component:
    id: str
    description: str
    default: bool
    recommended: bool
    size_estimate: str
    depends_on: List[str]
    files: List[Dict]

class ComponentResolver:
    def __init__(self, manifest_path: str):
        self.manifest = self._load_manifest(manifest_path)
        self.components = self._parse_components()

    def resolve_profile(self, profile_name: str) -> List[Component]:
        """Resolve all components for a profile"""
        profile = self.manifest['profiles'][profile_name]
        component_ids = profile['components']
        return self._resolve_dependencies(component_ids)

    def resolve_custom(self, selected_ids: List[str]) -> List[Component]:
        """Resolve custom selection with dependencies"""
        return self._resolve_dependencies(selected_ids)

    def _resolve_dependencies(self, component_ids: List[str]) -> List[Component]:
        """Resolve dependencies recursively"""
        resolved = set()
        queue = list(component_ids)

        while queue:
            comp_id = queue.pop(0)
            if comp_id in resolved:
                continue

            comp = self.components[comp_id]
            resolved.add(comp_id)

            # Add dependencies to queue
            for dep in comp.depends_on:
                if dep not in resolved:
                    queue.append(dep)

        # Return in dependency order
        return self._topological_sort(resolved)

    def _topological_sort(self, component_ids: Set[str]) -> List[Component]:
        """Sort components by dependencies"""
        # Implementation: Standard topological sort
        pass

    def validate_selection(self, components: List[Component]) -> Dict:
        """Validate component selection"""
        issues = []
        warnings = []

        for comp in components:
            # Check required dependencies
            for dep in comp.depends_on:
                if dep not in [c.id for c in components]:
                    issues.append(f"{comp.id} requires {dep}")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }
```

### 2. FileInstaller (Python)

**Purpose**: Copy files and create directories

```python
# scripts/file_installer.py

from pathlib import Path
import shutil
from typing import List

class FileInstaller:
    def __init__(self, source_repo: Path, target_repo: Path, dry_run: bool = False):
        self.source = source_repo
        self.target = target_repo
        self.dry_run = dry_run
        self.installed_files = []

    def install_component(self, component: Component) -> Dict:
        """Install a single component"""
        results = {
            "component": component.id,
            "files_installed": 0,
            "directories_created": 0,
            "errors": []
        }

        for file_spec in component.files:
            try:
                self._install_file(file_spec)
                results["files_installed"] += 1
            except Exception as e:
                results["errors"].append(str(e))

        return results

    def _install_file(self, file_spec: Dict):
        """Install a single file or directory"""
        source_path = self.source / file_spec['source']
        dest_path = self.target / file_spec['destination']

        if self.dry_run:
            print(f"Would install: {source_path} -> {dest_path}")
            return

        # Create parent directories
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        if source_path.is_dir():
            shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
        else:
            shutil.copy2(source_path, dest_path)

        self.installed_files.append(str(dest_path))

    def create_directories(self, directories: List[Dict]):
        """Create required directories"""
        for dir_spec in directories:
            dir_path = self.target / dir_spec['path']
            dir_path.mkdir(parents=True, exist_ok=True)

            if dir_spec.get('gitkeep'):
                (dir_path / '.gitkeep').touch()

    def generate_manifest(self, components: List[Component]) -> Dict:
        """Generate installation manifest"""
        return {
            "version": "2.0.0",
            "installed_at": datetime.now().isoformat(),
            "components": [c.id for c in components],
            "files": self.installed_files
        }
```

### 3. Validator (Python)

**Purpose**: Run post-installation validation

```python
# scripts/validator.py

import subprocess
from typing import List, Dict

class InstallationValidator:
    def __init__(self, target_repo: Path):
        self.target = target_repo

    def validate_profile(self, profile_name: str, manifest: Dict) -> Dict:
        """Run profile-specific validation"""
        validation_spec = manifest['validation']['profiles'][profile_name]
        results = {
            "profile": profile_name,
            "checks": [],
            "passed": 0,
            "failed": 0,
            "critical_failures": 0
        }

        for check in validation_spec['checks']:
            result = self._run_check(check)
            results["checks"].append(result)

            if result["passed"]:
                results["passed"] += 1
            else:
                results["failed"] += 1
                if check.get("critical"):
                    results["critical_failures"] += 1

        results["success"] = results["critical_failures"] == 0

        return results

    def _run_check(self, check: Dict) -> Dict:
        """Run a single validation check"""
        try:
            result = subprocess.run(
                check["test"],
                shell=True,
                cwd=self.target,
                capture_output=True,
                timeout=10
            )
            return {
                "name": check["name"],
                "passed": result.returncode == 0,
                "critical": check.get("critical", False),
                "output": result.stdout.decode() if result.stdout else None,
                "error": result.stderr.decode() if result.stderr else None
            }
        except Exception as e:
            return {
                "name": check["name"],
                "passed": False,
                "critical": check.get("critical", False),
                "error": str(e)
            }
```

### 4. CLI Interface (Bash)

**Purpose**: User-facing command line interface

```bash
#!/bin/bash
# scripts/install.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MANIFEST="$SCRIPT_DIR/components-v2.yaml"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

usage() {
    cat <<EOF
Scout-Plan-Build Framework Installer

USAGE:
    install.sh [OPTIONS]

OPTIONS:
    --profile=NAME          Install a predefined profile
                           (minimal, standard, full)

    --custom                Custom installation mode
    --select=COMPONENT      Select specific component (repeatable)

    --interactive           Interactive component selection UI

    --dry-run              Show what would be installed
    --yes                  Skip confirmation prompts
    --help                 Show this help message

PROFILES:
    minimal     300KB - Core commands only
    standard    400KB - Commands + automation (recommended)
    full        1.7MB - Everything including Python modules
    custom      Variable - Pick individual components

EXAMPLES:
    # Quick standard installation
    ./install.sh --profile=standard

    # Custom selection
    ./install.sh --custom \\
        --select=slash_commands.workflow.core \\
        --select=slash_commands.git.basic

    # Dry run to preview
    ./install.sh --profile=full --dry-run

    # Interactive mode
    ./install.sh --interactive
EOF
}

install_profile() {
    local profile="$1"
    local dry_run="${2:-false}"

    echo -e "${GREEN}Installing profile: $profile${NC}"

    # Call Python installer
    python3 "$SCRIPT_DIR/installer.py" \
        --manifest="$MANIFEST" \
        --profile="$profile" \
        --target="$REPO_ROOT" \
        $([ "$dry_run" = "true" ] && echo "--dry-run")

    if [ "$dry_run" = "false" ]; then
        # Run post-install scripts
        run_post_install "$profile"

        # Validate installation
        validate_installation "$profile"
    fi
}

install_custom() {
    local components=("$@")
    local dry_run="${DRY_RUN:-false}"

    echo -e "${GREEN}Custom installation${NC}"
    echo "Selected components:"
    for comp in "${components[@]}"; do
        echo "  - $comp"
    done

    # Call Python installer
    python3 "$SCRIPT_DIR/installer.py" \
        --manifest="$MANIFEST" \
        --custom \
        --select="${components[@]}" \
        --target="$REPO_ROOT" \
        $([ "$dry_run" = "true" ] && echo "--dry-run")
}

interactive_mode() {
    # Show TUI for component selection
    python3 "$SCRIPT_DIR/interactive_installer.py" \
        --manifest="$MANIFEST" \
        --target="$REPO_ROOT"
}

run_post_install() {
    local profile="$1"

    echo -e "${GREEN}Running post-install scripts...${NC}"

    # Make scripts executable
    chmod +x "$REPO_ROOT/scripts"/*.sh 2>/dev/null || true

    # Install Python dependencies if core_modules installed
    if [ -d "$REPO_ROOT/adws" ]; then
        echo "Installing Python dependencies..."
        cd "$REPO_ROOT"
        uv sync || pip install -r requirements.txt || echo "Install dependencies manually"
    fi

    # Test installation
    if [ -f "$REPO_ROOT/test_installation.py" ]; then
        echo "Testing installation..."
        python3 "$REPO_ROOT/test_installation.py" || {
            echo -e "${YELLOW}Warning: Installation test failed${NC}"
        }
    fi
}

validate_installation() {
    local profile="$1"

    echo -e "${GREEN}Validating installation...${NC}"

    python3 "$SCRIPT_DIR/validator.py" \
        --manifest="$MANIFEST" \
        --profile="$profile" \
        --target="$REPO_ROOT"
}

# Main entry point
main() {
    local profile=""
    local custom=false
    local interactive=false
    local dry_run=false
    local components=()

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --profile=*)
                profile="${1#*=}"
                shift
                ;;
            --custom)
                custom=true
                shift
                ;;
            --select=*)
                components+=("${1#*=}")
                shift
                ;;
            --interactive)
                interactive=true
                shift
                ;;
            --dry-run)
                dry_run=true
                shift
                ;;
            --help)
                usage
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done

    # Execute based on mode
    if [ "$interactive" = true ]; then
        interactive_mode
    elif [ "$custom" = true ]; then
        install_custom "${components[@]}"
    elif [ -n "$profile" ]; then
        install_profile "$profile" "$dry_run"
    else
        # Default to standard profile
        echo -e "${YELLOW}No profile specified, using 'standard' (recommended)${NC}"
        install_profile "standard" "$dry_run"
    fi
}

main "$@"
```

## Interactive UI (Optional)

Use `dialog` or Python `curses` for TUI:

```python
# scripts/interactive_installer.py

import curses
from typing import List, Set

class InteractiveInstaller:
    def __init__(self, manifest: Dict):
        self.manifest = manifest
        self.selected: Set[str] = set()

    def run(self):
        """Run interactive TUI"""
        curses.wrapper(self._main_loop)

    def _main_loop(self, stdscr):
        """Main curses loop"""
        curses.curs_set(0)  # Hide cursor
        current_row = 0

        while True:
            stdscr.clear()
            self._draw_header(stdscr)
            self._draw_components(stdscr, current_row)
            self._draw_footer(stdscr)

            key = stdscr.getch()

            if key == curses.KEY_UP and current_row > 0:
                current_row -= 1
            elif key == curses.KEY_DOWN:
                current_row += 1
            elif key == ord(' '):
                self._toggle_selection(current_row)
            elif key == ord('\n'):
                # Install selected
                break
            elif key == ord('q'):
                return

            stdscr.refresh()

    def _draw_components(self, stdscr, current_row: int):
        """Draw component list with checkboxes"""
        # Implementation: Draw tree view with selections
        pass
```

## Testing Strategy

### Unit Tests
```python
# tests/test_component_resolver.py

def test_resolve_minimal_profile():
    resolver = ComponentResolver("components-v2.yaml")
    components = resolver.resolve_profile("minimal")
    assert len(components) > 0
    assert "slash_commands.workflow.core" in [c.id for c in components]

def test_resolve_dependencies():
    resolver = ComponentResolver("components-v2.yaml")
    # Select worktree without scripts.worktree
    components = resolver.resolve_custom(["slash_commands.git.worktree"])
    # Should auto-include scripts.worktree
    assert "scripts.worktree" in [c.id for c in components]

def test_topological_sort():
    # A depends on B, B depends on C
    # Should return [C, B, A]
    pass
```

### Integration Tests
```bash
# tests/test_installation.sh

test_minimal_installation() {
    ./install.sh --profile=minimal --dry-run
    # Verify output shows correct files
}

test_custom_installation() {
    ./install.sh --custom \
        --select=slash_commands.workflow.core \
        --dry-run
}
```

## Implementation Phases

### Phase 1: Core (4 hours)
- ComponentResolver with dependency resolution
- FileInstaller with basic copying
- CLI interface with profile support

### Phase 2: Validation (2 hours)
- Validator with profile-specific checks
- Manifest generation
- Error handling

### Phase 3: Enhancement (2 hours)
- Interactive UI
- Progress indicators
- Rollback on failure

### Phase 4: Testing (2 hours)
- Unit tests
- Integration tests
- Documentation

## Success Criteria

- [ ] Install minimal profile (300KB)
- [ ] Install standard profile (400KB)
- [ ] Install full profile (1.7MB)
- [ ] Custom component selection works
- [ ] Dependencies auto-resolved
- [ ] Validation passes for each profile
- [ ] Dry-run mode shows preview
- [ ] Interactive UI functional
- [ ] Error handling graceful
- [ ] Documentation complete

---

**Status**: Ready for implementation
**Priority**: High (blocks v2 release)
**Dependencies**: None (components-v2.yaml complete)
