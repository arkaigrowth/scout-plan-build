#!/usr/bin/env python3
"""
Scout-Plan-Build Framework - Declarative Installer
Reads .scout_framework.yaml and installs in a reproducible, validated way
"""

import yaml
import os
import sys
import shutil
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class Colors:
    """Terminal colors for output"""
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


class FrameworkInstaller:
    """Declarative installer for Scout-Plan-Build framework"""

    def __init__(self, manifest_path: str, target_repo: str, dry_run: bool = False):
        """Initialize installer with manifest and target"""
        self.manifest_path = Path(manifest_path)
        self.target = Path(target_repo).resolve()
        self.source = self.manifest_path.parent
        self.dry_run = dry_run
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.installed_files: List[str] = []

        # Load manifest
        try:
            with open(self.manifest_path) as f:
                self.manifest = yaml.safe_load(f)
        except Exception as e:
            print(f"{Colors.RED}❌ Failed to load manifest: {e}{Colors.NC}")
            sys.exit(1)

    def log(self, message: str, color: str = Colors.NC):
        """Print colored log message"""
        print(f"{color}{message}{Colors.NC}")

    def check_requirements(self) -> bool:
        """Validate system requirements"""
        self.log("\n🔍 Checking requirements...", Colors.BLUE)

        all_met = True
        for tool, config in self.manifest['requirements'].items():
            version_req = config.get('version', '')
            command = config.get('command', f'{tool} --version')
            optional = config.get('optional', False)

            try:
                result = subprocess.run(
                    command.split(),
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode == 0:
                    self.log(f"  ✅ {tool} found", Colors.GREEN)
                else:
                    raise subprocess.CalledProcessError(result.returncode, command)

            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                if optional:
                    self.warnings.append(f"Optional tool not found: {tool}")
                    self.log(f"  ⚠️  {tool} not found (optional)", Colors.YELLOW)
                    if config.get('note'):
                        self.log(f"     Note: {config['note']}", Colors.YELLOW)
                else:
                    self.errors.append(f"Required tool not found: {tool}")
                    self.log(f"  ❌ {tool} not found (required)", Colors.RED)
                    all_met = False

        return all_met

    def install_components(self):
        """Install framework components"""
        self.log("\n📦 Installing components...", Colors.BLUE)

        for name, config in self.manifest['components'].items():
            self.log(f"  Installing {name}...", Colors.NC)

            source = self.source / config['source']
            dest = self.target / config['destination']

            if not self.dry_run:
                dest.mkdir(parents=True, exist_ok=True)

            files_to_copy = config.get('files', [])

            if files_to_copy == 'all':
                # Copy entire directory
                if source.exists():
                    if not self.dry_run:
                        shutil.copytree(source, dest, dirs_exist_ok=True)
                    self.log(f"    ✅ Copied {source} → {dest}", Colors.GREEN)
                    self.installed_files.append(str(dest))
                elif config.get('required', True):
                    self.errors.append(f"Required component missing: {source}")
                    self.log(f"    ❌ Source not found: {source}", Colors.RED)
            elif files_to_copy:
                # Copy specific files
                for file in files_to_copy:
                    src_file = source / file if source.is_dir() else self.source / config['source'] / file

                    if src_file.exists():
                        if not self.dry_run:
                            shutil.copy2(src_file, dest / file)
                        self.log(f"    ✅ {file}", Colors.GREEN)
                        self.installed_files.append(str(dest / file))
                    elif config.get('required', True):
                        self.errors.append(f"Required file missing: {file}")
                        self.log(f"    ❌ Missing: {file}", Colors.RED)

    def create_directories(self):
        """Create required directory structure"""
        self.log("\n📁 Creating directory structure...", Colors.BLUE)

        for dir_config in self.manifest['directories']:
            path = self.target / dir_config['path']

            if not self.dry_run:
                path.mkdir(parents=True, exist_ok=True)

                # Create .gitkeep if requested
                if dir_config.get('gitkeep'):
                    (path / '.gitkeep').touch()

            self.log(f"  ✅ {dir_config['path']} - {dir_config['description']}", Colors.GREEN)

    def generate_configurations(self):
        """Generate configuration files"""
        self.log("\n⚙️  Generating configuration files...", Colors.BLUE)

        # Detect repo name
        repo_name = self.target.name

        for config in self.manifest['configurations']:
            file_path = self.target / config['file']

            # Skip if file exists and overwrite is False
            if file_path.exists() and not config.get('overwrite', False):
                self.log(f"  ⏭️  {config['file']} (exists, skipping)", Colors.YELLOW)
                continue

            if config.get('auto_generate'):
                # Auto-generate from content template
                content = config.get('content', '')
                content = content.replace('${REPO_NAME}', repo_name)
                content = content.replace('${FRAMEWORK_VERSION}', self.manifest['framework_version'])

                if not self.dry_run:
                    file_path.write_text(content)

                self.log(f"  ✅ {config['file']} (generated)", Colors.GREEN)

            elif config.get('template'):
                # Copy from template
                template = self.source / config['template']
                if template.exists():
                    if not self.dry_run:
                        shutil.copy2(template, file_path)
                    self.log(f"  ✅ {config['file']} (from template)", Colors.GREEN)
                else:
                    self.warnings.append(f"Template not found: {template}")

            elif config.get('source'):
                # Copy from source file
                source = self.source / config['source']
                if source.exists():
                    if not self.dry_run:
                        shutil.copy2(source, file_path)
                    self.log(f"  ✅ {config['file']} (copied)", Colors.GREEN)

            self.installed_files.append(str(file_path))

    def setup_environment(self):
        """Set up environment variables in .env"""
        self.log("\n🔐 Setting up environment...", Colors.BLUE)

        env_file = self.target / '.env'
        env_vars = {}

        # Load existing .env if present
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        env_vars[key] = value

        # Add/update from manifest
        for var_config in self.manifest['environment']['variables']:
            name = var_config['name']
            value = var_config['value']

            # Expand environment variables
            if value.startswith('${') and value.endswith('}'):
                env_var = value[2:-1]
                value = os.getenv(env_var, value)

            # Only set if required or not already present
            if var_config.get('required') and name not in env_vars:
                env_vars[name] = value
                self.log(f"  ✅ {name}", Colors.GREEN)
            elif name in env_vars:
                self.log(f"  ⏭️  {name} (already set)", Colors.YELLOW)
            else:
                env_vars[name] = value
                self.log(f"  ✅ {name} (optional)", Colors.GREEN)

        # Write .env
        if not self.dry_run:
            with open(env_file, 'w') as f:
                f.write("# Scout-Plan-Build Framework Environment\n")
                f.write(f"# Generated: {datetime.now().isoformat()}\n\n")
                for key, value in env_vars.items():
                    f.write(f"{key}={value}\n")

    def run_validation(self) -> bool:
        """Run post-installation validation checks"""
        self.log("\n✅ Running validation checks...", Colors.BLUE)

        if self.dry_run:
            self.log("  ⏭️  Skipping validation in dry-run mode", Colors.YELLOW)
            return True

        failed_critical = False

        for check in self.manifest['validation']['checks']:
            try:
                result = subprocess.run(
                    check['test'],
                    shell=True,
                    cwd=self.target,
                    capture_output=True,
                    timeout=30
                )

                if result.returncode == 0:
                    self.log(f"  ✅ {check['name']}", Colors.GREEN)
                else:
                    if check['critical']:
                        self.errors.append(f"Critical validation failed: {check['name']}")
                        self.log(f"  ❌ {check['name']} (critical)", Colors.RED)
                        failed_critical = True
                    else:
                        self.warnings.append(f"Validation warning: {check['name']}")
                        self.log(f"  ⚠️  {check['name']}", Colors.YELLOW)

            except subprocess.TimeoutExpired:
                self.warnings.append(f"Validation timeout: {check['name']}")
                self.log(f"  ⏱️  {check['name']} (timeout)", Colors.YELLOW)

            except Exception as e:
                self.log(f"  ⚠️  {check['name']} - {e}", Colors.YELLOW)
                if check['critical']:
                    failed_critical = True

        return not failed_critical

    def run_post_install(self):
        """Run post-installation tasks"""
        self.log("\n🚀 Running post-installation tasks...", Colors.BLUE)

        if self.dry_run:
            self.log("  ⏭️  Skipping post-install in dry-run mode", Colors.YELLOW)
            return

        for task in self.manifest.get('post_install', []):
            # Check conditional
            if task.get('conditional'):
                if not self.check_conditional(task['conditional']):
                    self.log(f"  ⏭️  {task['name']} (condition not met)", Colors.YELLOW)
                    continue

            self.log(f"  🔄 {task['name']}...", Colors.NC)

            try:
                result = subprocess.run(
                    task['command'],
                    shell=True,
                    cwd=self.target,
                    capture_output=True,
                    text=True,
                    timeout=120
                )

                if result.returncode == 0:
                    self.log(f"  ✅ {task['name']}", Colors.GREEN)
                else:
                    if task.get('optional', False):
                        self.log(f"  ⚠️  {task['name']} (optional, failed)", Colors.YELLOW)
                    else:
                        self.errors.append(f"Post-install failed: {task['name']}")
                        self.log(f"  ❌ {task['name']}", Colors.RED)

            except subprocess.TimeoutExpired:
                self.log(f"  ⏱️  {task['name']} (timeout)", Colors.YELLOW)

            except Exception as e:
                if not task.get('optional', False):
                    self.errors.append(f"Post-install error: {task['name']} - {e}")
                    self.log(f"  ❌ {task['name']}: {e}", Colors.RED)

    def check_conditional(self, condition: str) -> bool:
        """Check if a conditional requirement is met"""
        if condition == "git_repo":
            return (self.target / '.git').exists()
        elif condition == "python_project":
            return (self.target / 'pyproject.toml').exists() or (self.target / 'setup.py').exists()
        elif condition == "git_repo_and_changes":
            if not (self.target / '.git').exists():
                return False
            # Check if there are changes to commit
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.target,
                capture_output=True,
                text=True
            )
            return bool(result.stdout.strip())
        return True

    def generate_installation_receipt(self):
        """Generate receipt of what was installed"""
        receipt_file = self.target / '.scout_installation.json'

        receipt = {
            "framework_version": self.manifest['framework_version'],
            "installed_at": datetime.now().isoformat(),
            "installed_files": self.installed_files,
            "warnings": self.warnings,
            "manifest_version": self.manifest['version']
        }

        if not self.dry_run:
            with open(receipt_file, 'w') as f:
                json.dump(receipt, f, indent=2)

        return receipt

    def install(self) -> bool:
        """Execute complete installation"""
        self.log("=" * 60, Colors.BLUE)
        self.log("🚀 Scout-Plan-Build Framework - Declarative Installer", Colors.BLUE)
        self.log("=" * 60, Colors.BLUE)
        self.log(f"\nFramework: {self.manifest['metadata']['name']}")
        self.log(f"Version: {self.manifest['framework_version']}")
        self.log(f"Target: {self.target}")
        if self.dry_run:
            self.log("\n⚠️  DRY RUN MODE - No changes will be made\n", Colors.YELLOW)

        # Check if target exists
        if not self.target.exists():
            self.log(f"\n❌ Target directory does not exist: {self.target}", Colors.RED)
            return False

        # Run installation steps
        if not self.check_requirements():
            self.print_summary(success=False)
            return False

        self.install_components()
        self.create_directories()
        self.generate_configurations()
        self.setup_environment()

        if not self.run_validation():
            self.print_summary(success=False)
            return False

        self.run_post_install()

        # Generate receipt
        receipt = self.generate_installation_receipt()

        # Summary
        self.print_summary(success=True)
        return True

    def print_summary(self, success: bool):
        """Print installation summary"""
        self.log("\n" + "=" * 60, Colors.BLUE)

        if success:
            self.log("✅ INSTALLATION SUCCESSFUL!", Colors.GREEN)

            self.log(f"\n📦 Installed {len(self.installed_files)} files", Colors.GREEN)

            if self.warnings:
                self.log(f"\n⚠️  {len(self.warnings)} Warnings:", Colors.YELLOW)
                for warning in self.warnings:
                    self.log(f"  • {warning}", Colors.YELLOW)

            self.log("\n📚 Next Steps:", Colors.BLUE)
            self.log(f"  1. cd {self.target}")
            self.log("  2. Review CLAUDE.md for usage instructions")
            self.log("  3. Edit .env with your API keys")
            self.log("  4. Run: export $(grep -v '^#' .env | xargs)")
            self.log("  5. Test: ./scripts/validate_pipeline.sh")

        else:
            self.log("❌ INSTALLATION FAILED", Colors.RED)

            if self.errors:
                self.log(f"\n❌ {len(self.errors)} Errors:", Colors.RED)
                for error in self.errors:
                    self.log(f"  • {error}", Colors.RED)

            if self.warnings:
                self.log(f"\n⚠️  {len(self.warnings)} Warnings:", Colors.YELLOW)
                for warning in self.warnings:
                    self.log(f"  • {warning}", Colors.YELLOW)

        self.log("=" * 60, Colors.BLUE)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Scout-Plan-Build Framework - Declarative Installer"
    )
    parser.add_argument(
        'target_repo',
        help="Path to target repository"
    )
    parser.add_argument(
        '--manifest',
        default='.scout_framework.yaml',
        help="Path to manifest file (default: .scout_framework.yaml)"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Show what would be installed without making changes"
    )
    parser.add_argument(
        '--verify',
        action='store_true',
        help="Run additional verification checks"
    )

    args = parser.parse_args()

    # Find manifest relative to this script
    script_dir = Path(__file__).parent.parent
    manifest_path = script_dir / args.manifest

    if not manifest_path.exists():
        print(f"{Colors.RED}❌ Manifest not found: {manifest_path}{Colors.NC}")
        sys.exit(1)

    # Run installer
    installer = FrameworkInstaller(
        manifest_path=str(manifest_path),
        target_repo=args.target_repo,
        dry_run=args.dry_run
    )

    success = installer.install()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
