# Python Import Trace Summary

**Run:** Sun Nov 23 20:38:30 CST 2025
**Environment:** local
**Directory:** .
**Output:** /Users/alexkamysz/AI/scout_plan_build_mvp/scout_outputs/traces/20251123_203826/python_imports.json

## Statistics

- Total imports: 384
- Valid imports: 291
  - Installed packages: 290
  - Local modules: 1
- Broken imports: 93

## Broken Imports

- `scripts/install_declarative.py:6` → `yaml` (type: import)
- `tests/test_bitbucket_integration.py:3` → `pytest` (type: import)
- `adws/adw_triggers/trigger_cron.py:28` → `schedule` (type: import)
- `adws/adw_modules/r2_uploader.py:6` → `boto3` (type: import)
- `adws/adw_tests/test_validators.py:11` → `pytest` (type: import)
- `benchmarks/parallel_test_suite.py:14` → `psutil` (type: import)
- `benchmarks/parallel_test_suite.py:21` → `pytest` (type: import)
- `ai_docs/architecture/diagrams/architecture-viewer.html:18` → `mermaid` (type: import)
- `adws/adw_plan_build.py:23` → `adw_modules.workflow_ops` (type: from_import)
- `adws/adw_tests/test_agents.py:20` → `adw_modules.data_types` (type: from_import)
- `adws/adw_tests/test_agents.py:21` → `adw_modules.agent` (type: from_import)
- `adws/adw_tests/test_agents.py:22` → `adw_modules.utils` (type: from_import)
- `adws/adw_sdlc.py:26` → `adw_modules.workflow_ops` (type: from_import)
- `adws/adw_patch.py:32` → `adw_modules.state` (type: from_import)
- `adws/adw_patch.py:33` → `adw_modules.git_ops` (type: from_import)
- `adws/adw_patch.py:50` → `adw_modules.utils` (type: from_import)
- `adws/adw_patch.py:56` → `adw_modules.agent` (type: from_import)
- `adws/adw_modules/state.py:11` → `adw_modules.data_types` (type: from_import)
- `adws/adw_modules/state.py:12` → `adw_modules.exceptions` (type: from_import)
- `adws/adw_plan_build_test.py:24` → `adw_modules.workflow_ops` (type: from_import)
- `adws/adw_tests/health_check.py:39` → `adw_modules.github` (type: from_import)
- `adws/adw_tests/health_check.py:40` → `adw_modules.utils` (type: from_import)
- `adws/adw_plan_build_test_review.py:25` → `adw_modules.workflow_ops` (type: from_import)
- `adws/adw_build.py:26` → `adw_modules.state` (type: from_import)
- `adws/adw_build.py:27` → `adw_modules.git_ops` (type: from_import)
- `adws/adw_build.py:28` → `adw_modules.github` (type: from_import)
- `adws/adw_build.py:35` → `adw_modules.utils` (type: from_import)
- `adws/adw_build.py:36` → `adw_modules.data_types` (type: from_import)
- `adws/adw_build.py:184` → `adw_modules.workflow_ops` (type: from_import)
- `adws/adw_plan_build_document.py:28` → `adw_modules.workflow_ops` (type: from_import)
- `adws/adw_tests/sandbox_poc.py:31` → `e2b_code_interpreter` (type: from_import)
- `adws/adw_modules/validators.py:21` → `.constants` (type: from_import)
- `adws/adw_document.py:27` → `adw_modules.state` (type: from_import)
- `adws/adw_document.py:28` → `adw_modules.git_ops` (type: from_import)
- `adws/adw_document.py:29` → `adw_modules.github` (type: from_import)
- `adws/adw_document.py:35` → `adw_modules.utils` (type: from_import)
- `adws/adw_document.py:36` → `adw_modules.data_types` (type: from_import)
- `adws/adw_document.py:37` → `adw_modules.agent` (type: from_import)
- `adws/adw_triggers/trigger_cron.py:33` → `adw_modules.utils` (type: from_import)
- `adws/adw_triggers/trigger_cron.py:35` → `adw_modules.github` (type: from_import)
- `adws/adw_plan_build_review.py:27` → `adw_modules.workflow_ops` (type: from_import)
- `adws/adw_modules/r2_uploader.py:7` → `botocore.client` (type: from_import)
- `adws/adw_modules/r2_uploader.py:8` → `botocore.exceptions` (type: from_import)
- `adws/adw_modules/workflow_ops.py:17` → `adw_modules.agent` (type: from_import)
- `adws/adw_modules/workflow_ops.py:18` → `adw_modules.github` (type: from_import)
- `adws/adw_modules/workflow_ops.py:19` → `adw_modules.state` (type: from_import)
- `adws/adw_modules/workflow_ops.py:20` → `adw_modules.utils` (type: from_import)
- `adws/adw_modules/workflow_ops.py:480` → `adw_modules.data_types` (type: from_import)
- `adws/adw_modules/workflow_ops.py:522` → `adw_modules.git_ops` (type: from_import)
- `adws/adw_modules/workflow_ops.py:579` → `adw_modules.utils` (type: from_import)
- `adws/adw_modules/workflow_ops.py:670` → `adw_modules.git_ops` (type: from_import)
- `adws/adw_modules/workflow_ops.py:718` → `adw_modules.git_ops` (type: from_import)
- `adws/adw_modules/git_ops.py:13` → `adw_modules.github` (type: from_import)
- `adws/adw_modules/git_ops.py:14` → `adw_modules.exceptions` (type: from_import)
- `adws/adw_modules/git_ops.py:15` → `adw_modules.validators` (type: from_import)
- `adws/adw_modules/git_ops.py:16` → `adw_modules.vcs_detection` (type: from_import)
- `adws/adw_modules/git_ops.py:154` → `adw_modules` (type: from_import)
- `adws/adw_modules/git_ops.py:308` → `adw_modules.exceptions` (type: from_import)
- `adws/adw_modules/git_ops.py:369` → `adw_modules.github` (type: from_import)
- `adws/adw_modules/git_ops.py:372` → `adw_modules.workflow_ops` (type: from_import)
- `adws/scout_simple.py:13` → `adw_modules.constants` (type: from_import)
- `adws/adw_modules/agent.py:181` → `.utils` (type: from_import)
- `adws/adw_tests/test_adw_test_e2e.py:21` → `adw_test` (type: from_import)
- `adws/adw_tests/test_adw_test_e2e.py:22` → `adw_modules.data_types` (type: from_import)
- `adws/adw_tests/test_adw_test_e2e.py:23` → `adw_modules.utils` (type: from_import)
- `adws/adw_triggers/trigger_webhook.py:25` → `fastapi` (type: from_import)
- `adws/adw_triggers/trigger_webhook.py:32` → `adw_modules.utils` (type: from_import)
- `adws/adw_triggers/trigger_webhook.py:33` → `adw_modules.github` (type: from_import)
- `adws/adw_triggers/trigger_webhook.py:34` → `adw_modules.workflow_ops` (type: from_import)
- `adws/adw_triggers/trigger_webhook.py:35` → `adw_modules.state` (type: from_import)
- `adws/adw_scout_parallel.py:17` → `adw_modules.utils` (type: from_import)
- `adws/adw_scout_parallel.py:18` → `adw_modules.constants` (type: from_import)
- `adws/adw_modules/exceptions.py:432` → `adw_modules.github` (type: from_import)
- `adws/adw_modules/exceptions.py:433` → `adw_modules.workflow_ops` (type: from_import)
- `adws/adw_modules/memory_hooks.py:26` → `adw_modules.memory_manager` (type: from_import)
- `adws/adw_modules/memory_hooks.py:107` → `adw_modules.github` (type: from_import)
- `adws/adw_tests/test_r2_uploader.py:29` → `adw_modules.r2_uploader` (type: from_import)
- `adws/adw_plan.py:27` → `adw_modules.state` (type: from_import)
- `adws/adw_plan.py:28` → `adw_modules.git_ops` (type: from_import)
- `adws/adw_plan.py:44` → `adw_modules.utils` (type: from_import)
- `adws/adw_plan.py:45` → `adw_modules.data_types` (type: from_import)
- `adws/adw_modules/github.py:20` → `.data_types` (type: from_import)
- `adws/adw_modules/github.py:21` → `.exceptions` (type: from_import)
- `adws/adw_review.py:31` → `adw_modules.state` (type: from_import)
- `adws/adw_review.py:32` → `adw_modules.git_ops` (type: from_import)
- `adws/adw_review.py:48` → `adw_modules.utils` (type: from_import)
- `adws/adw_review.py:56` → `adw_modules.agent` (type: from_import)
- `adws/adw_review.py:57` → `adw_modules.r2_uploader` (type: from_import)
- `adws/adw_test.py:39` → `adw_modules.agent` (type: from_import)
- `adws/adw_test.py:46` → `adw_modules.utils` (type: from_import)
- `adws/adw_test.py:47` → `adw_modules.state` (type: from_import)
- `adws/adw_test.py:48` → `adw_modules.git_ops` (type: from_import)
- `adws/adw_test.py:911` → `adw_modules.git_ops` (type: from_import)

## Suggested Fixes

### `.constants`

**Files using this module:**
- adws/adw_modules/validators.py:21

**Possible fix:**
```bash
pip install .constants --break-system-packages
# or add to requirements.txt
```

### `.data_types`

**Files using this module:**
- adws/adw_modules/github.py:20

**Possible fix:**
```bash
pip install .data_types --break-system-packages
# or add to requirements.txt
```

### `.exceptions`

**Files using this module:**
- adws/adw_modules/github.py:21

**Possible fix:**
```bash
pip install .exceptions --break-system-packages
# or add to requirements.txt
```

### `.utils`

**Files using this module:**
- adws/adw_modules/agent.py:181

**Possible fix:**
```bash
pip install .utils --break-system-packages
# or add to requirements.txt
```

### `adw_modules`

**Files using this module:**
- adws/adw_modules/git_ops.py:154

**Possible fix:**
```bash
pip install adw_modules --break-system-packages
# or add to requirements.txt
```

### `adw_modules.agent`

**Files using this module:**
- adws/adw_tests/test_agents.py:21
- adws/adw_patch.py:56
- adws/adw_document.py:37
- adws/adw_modules/workflow_ops.py:17
- adws/adw_review.py:56
- adws/adw_test.py:39

**Possible fix:**
```bash
pip install adw_modules.agent --break-system-packages
# or add to requirements.txt
```

### `adw_modules.constants`

**Files using this module:**
- adws/scout_simple.py:13
- adws/adw_scout_parallel.py:18

**Possible fix:**
```bash
pip install adw_modules.constants --break-system-packages
# or add to requirements.txt
```

### `adw_modules.data_types`

**Files using this module:**
- adws/adw_tests/test_agents.py:20
- adws/adw_modules/state.py:11
- adws/adw_build.py:36
- adws/adw_document.py:36
- adws/adw_modules/workflow_ops.py:480
- adws/adw_tests/test_adw_test_e2e.py:22
- adws/adw_plan.py:45

**Possible fix:**
```bash
pip install adw_modules.data_types --break-system-packages
# or add to requirements.txt
```

### `adw_modules.exceptions`

**Files using this module:**
- adws/adw_modules/state.py:12
- adws/adw_modules/git_ops.py:14
- adws/adw_modules/git_ops.py:308

**Possible fix:**
```bash
pip install adw_modules.exceptions --break-system-packages
# or add to requirements.txt
```

### `adw_modules.git_ops`

**Files using this module:**
- adws/adw_patch.py:33
- adws/adw_build.py:27
- adws/adw_document.py:28
- adws/adw_modules/workflow_ops.py:522
- adws/adw_modules/workflow_ops.py:670
- adws/adw_modules/workflow_ops.py:718
- adws/adw_plan.py:28
- adws/adw_review.py:32
- adws/adw_test.py:48
- adws/adw_test.py:911

**Possible fix:**
```bash
pip install adw_modules.git_ops --break-system-packages
# or add to requirements.txt
```

### `adw_modules.github`

**Files using this module:**
- adws/adw_tests/health_check.py:39
- adws/adw_build.py:28
- adws/adw_document.py:29
- adws/adw_triggers/trigger_cron.py:35
- adws/adw_modules/workflow_ops.py:18
- adws/adw_modules/git_ops.py:13
- adws/adw_modules/git_ops.py:369
- adws/adw_triggers/trigger_webhook.py:33
- adws/adw_modules/exceptions.py:432
- adws/adw_modules/memory_hooks.py:107

**Possible fix:**
```bash
pip install adw_modules.github --break-system-packages
# or add to requirements.txt
```

### `adw_modules.memory_manager`

**Files using this module:**
- adws/adw_modules/memory_hooks.py:26

**Possible fix:**
```bash
pip install adw_modules.memory_manager --break-system-packages
# or add to requirements.txt
```

### `adw_modules.r2_uploader`

**Files using this module:**
- adws/adw_tests/test_r2_uploader.py:29
- adws/adw_review.py:57

**Possible fix:**
```bash
pip install adw_modules.r2_uploader --break-system-packages
# or add to requirements.txt
```

### `adw_modules.state`

**Files using this module:**
- adws/adw_patch.py:32
- adws/adw_build.py:26
- adws/adw_document.py:27
- adws/adw_modules/workflow_ops.py:19
- adws/adw_triggers/trigger_webhook.py:35
- adws/adw_plan.py:27
- adws/adw_review.py:31
- adws/adw_test.py:47

**Possible fix:**
```bash
pip install adw_modules.state --break-system-packages
# or add to requirements.txt
```

### `adw_modules.utils`

**Files using this module:**
- adws/adw_tests/test_agents.py:22
- adws/adw_patch.py:50
- adws/adw_tests/health_check.py:40
- adws/adw_build.py:35
- adws/adw_document.py:35
- adws/adw_triggers/trigger_cron.py:33
- adws/adw_modules/workflow_ops.py:20
- adws/adw_modules/workflow_ops.py:579
- adws/adw_tests/test_adw_test_e2e.py:23
- adws/adw_triggers/trigger_webhook.py:32
- adws/adw_scout_parallel.py:17
- adws/adw_plan.py:44
- adws/adw_review.py:48
- adws/adw_test.py:46

**Possible fix:**
```bash
pip install adw_modules.utils --break-system-packages
# or add to requirements.txt
```

### `adw_modules.validators`

**Files using this module:**
- adws/adw_modules/git_ops.py:15

**Possible fix:**
```bash
pip install adw_modules.validators --break-system-packages
# or add to requirements.txt
```

### `adw_modules.vcs_detection`

**Files using this module:**
- adws/adw_modules/git_ops.py:16

**Possible fix:**
```bash
pip install adw_modules.vcs_detection --break-system-packages
# or add to requirements.txt
```

### `adw_modules.workflow_ops`

**Files using this module:**
- adws/adw_plan_build.py:23
- adws/adw_sdlc.py:26
- adws/adw_plan_build_test.py:24
- adws/adw_plan_build_test_review.py:25
- adws/adw_build.py:184
- adws/adw_plan_build_document.py:28
- adws/adw_plan_build_review.py:27
- adws/adw_modules/git_ops.py:372
- adws/adw_triggers/trigger_webhook.py:34
- adws/adw_modules/exceptions.py:433

**Possible fix:**
```bash
pip install adw_modules.workflow_ops --break-system-packages
# or add to requirements.txt
```

### `adw_test`

**Files using this module:**
- adws/adw_tests/test_adw_test_e2e.py:21

**Possible fix:**
```bash
pip install adw_test --break-system-packages
# or add to requirements.txt
```

### `boto3`

**Files using this module:**
- adws/adw_modules/r2_uploader.py:6

**Possible fix:**
```bash
pip install boto3 --break-system-packages
# or add to requirements.txt
```

### `botocore.client`

**Files using this module:**
- adws/adw_modules/r2_uploader.py:7

**Possible fix:**
```bash
pip install botocore.client --break-system-packages
# or add to requirements.txt
```

### `botocore.exceptions`

**Files using this module:**
- adws/adw_modules/r2_uploader.py:8

**Possible fix:**
```bash
pip install botocore.exceptions --break-system-packages
# or add to requirements.txt
```

### `e2b_code_interpreter`

**Files using this module:**
- adws/adw_tests/sandbox_poc.py:31

**Possible fix:**
```bash
pip install e2b_code_interpreter --break-system-packages
# or add to requirements.txt
```

### `fastapi`

**Files using this module:**
- adws/adw_triggers/trigger_webhook.py:25

**Possible fix:**
```bash
pip install fastapi --break-system-packages
# or add to requirements.txt
```

### `mermaid`

**Files using this module:**
- ai_docs/architecture/diagrams/architecture-viewer.html:18

**Possible fix:**
```bash
pip install mermaid --break-system-packages
# or add to requirements.txt
```

### `psutil`

**Files using this module:**
- benchmarks/parallel_test_suite.py:14

**Possible fix:**
```bash
pip install psutil --break-system-packages
# or add to requirements.txt
```

### `pytest`

**Files using this module:**
- tests/test_bitbucket_integration.py:3
- adws/adw_tests/test_validators.py:11
- benchmarks/parallel_test_suite.py:21

**Possible fix:**
```bash
pip install pytest --break-system-packages
# or add to requirements.txt
```

### `schedule`

**Files using this module:**
- adws/adw_triggers/trigger_cron.py:28

**Possible fix:**
```bash
pip install schedule --break-system-packages
# or add to requirements.txt
```

### `yaml`

**Files using this module:**
- scripts/install_declarative.py:6

**Possible fix:**
```bash
pip install yaml --break-system-packages
# or add to requirements.txt
```

