# Python Import Trace Summary

**Run:** Sun Nov 23 21:51:02 CST 2025
**Environment:** local
**Directory:** adws
**Output:** /Users/alexkamysz/AI/scout_plan_build_mvp/scout_outputs/traces/20251123_215059/python_imports.json

## Statistics

- Total imports: 324
- Valid imports: 312
  - Installed packages: 235
  - Local modules: 77
- Broken imports: 12

## Broken Imports

- `adws/adw_triggers/trigger_cron.py:28` → `schedule` (type: import)
- `adws/adw_tests/test_validators.py:11` → `pytest` (type: import)
- `adws/adw_modules/r2_uploader.py:6` → `boto3` (type: import)
- `adws/adw_tests/sandbox_poc.py:31` → `e2b_code_interpreter` (type: from_import)
- `adws/adw_fix_dependencies.py:54` → `adws.adw_modules.state` (type: from_import)
- `adws/adw_modules/r2_uploader.py:7` → `botocore.client` (type: from_import)
- `adws/adw_modules/r2_uploader.py:8` → `botocore.exceptions` (type: from_import)
- `adws/adw_triggers/trigger_webhook.py:25` → `fastapi` (type: from_import)
- `adws/adw_modules/github.py:20` → `.data_types` (type: from_import)
- `adws/adw_modules/github.py:21` → `.exceptions` (type: from_import)
- `adws/adw_modules/validators.py:21` → `.constants` (type: from_import)
- `adws/adw_modules/agent.py:181` → `.utils` (type: from_import)

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

### `adws.adw_modules.state`

**Files using this module:**
- adws/adw_fix_dependencies.py:54

**Possible fix:**
```bash
pip install adws.adw_modules.state --break-system-packages
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

### `pytest`

**Files using this module:**
- adws/adw_tests/test_validators.py:11

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

