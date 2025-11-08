# Security Audit Report - scout_plan_build_mvp

**Audit Date**: 2025-10-27
**Auditor**: Security Analysis Team
**Severity Levels**: 🔴 CRITICAL | 🟡 HIGH | 🟠 MEDIUM | 🟢 LOW

## Executive Summary

The scout_plan_build_mvp codebase has implemented several security measures including Pydantic validation, filtered environment variables, and command injection prevention. However, several critical vulnerabilities must be addressed before public release.

## 🔴 CRITICAL Issues (Must Fix Before Public Release)

### 1. Command Injection Vulnerability in scout_simple.py
**File**: `/adws/scout_simple.py`
**Lines**: 26-31, 42-48

```python
# VULNERABLE CODE - Direct shell command with user input
result = subprocess.run(
    ["grep", "-r", "-l", keyword, ".", "--include=*.py", "--include=*.js"],
    capture_output=True,
    text=True,
    cwd=".",
    timeout=5
)
```

**Risk**: The `keyword` variable comes directly from user input without validation. Special characters could break out of the grep command.

**Fix Required**:
```python
import shlex
# Sanitize keyword before use
safe_keyword = shlex.quote(keyword)
```

### 2. Webhook Endpoint Without Authentication
**File**: `/adws/adw_triggers/trigger_webhook.py`
**Lines**: 50-51

```python
@app.post("/gh-webhook")
async def github_webhook(request: Request):
```

**Risk**: The webhook endpoint has no authentication mechanism. Anyone can trigger ADW workflows by sending crafted requests.

**Fix Required**:
- Implement GitHub webhook signature verification (HMAC-SHA256)
- Add webhook secret to environment variables
- Verify X-Hub-Signature-256 header

### 3. Unvalidated JSON Parsing in Webhook
**File**: `/adws/adw_triggers/trigger_webhook.py`
**Line**: 58

```python
payload = await request.json()
```

**Risk**: No size limits or validation on incoming JSON payload. Could lead to DoS attacks.

**Fix Required**:
- Add request size limits
- Validate payload structure before processing
- Add rate limiting

## 🟡 HIGH Priority Issues

### 4. Environment Variable Exposure Risk
**File**: `/adws/adw_modules/utils.py`
**Lines**: 171-215

While the code filters environment variables through `get_safe_subprocess_env()`, it still passes sensitive tokens to subprocesses:

```python
"ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
"GITHUB_PAT": os.getenv("GITHUB_PAT"),
```

**Risk**: Subprocess logs or errors might expose these tokens.

**Recommendation**:
- Never pass API keys through environment variables to subprocesses
- Use secure credential storage mechanisms
- Implement token rotation strategy

### 5. Insufficient Path Traversal Protection
**File**: `/adws/adw_modules/validators.py`
**Lines**: 129-134

```python
if '..' in v:
    raise ValueError("Directory traversal (..) not allowed in file path")
```

**Risk**: This check can be bypassed using symlinks or absolute paths.

**Fix Required**:
- Use `Path.resolve()` and verify against allowed base directories
- Check for symlink attacks
- Validate absolute paths more strictly

### 6. Command Argument Validation Bypass
**File**: `/adws/adw_modules/validators.py`
**Lines**: 310-311

```python
validated_args.append(shlex.quote(arg))
```

**Issue**: While `shlex.quote()` is used, the validated args are stored but the original subprocess calls don't always use these validated arguments.

## 🟠 MEDIUM Priority Issues

### 7. Git Operations Without Branch Protection
**File**: `/adws/adw_modules/git_ops.py`

The code allows operations on any branch without checking if it's a protected branch (main/master).

**Risk**: Accidental or malicious commits to protected branches.

**Fix Required**:
- Add protected branch list
- Prevent operations on protected branches
- Implement branch name validation

### 8. Logging Sensitive Information
**File**: `/adws/adw_modules/memory_hooks.py`
**Lines**: 52-73

While the code attempts to sanitize logs, the regex patterns are incomplete:

```python
r'api_key["\']?\s*[:=]\s*["\']?[\w-]+'
```

**Risk**: Doesn't catch all API key formats (e.g., base64 encoded, different naming conventions).

### 9. subprocess.run Without Shell Protection
**File**: `/adws/adw_common.py`
**Line**: 17

```python
return subprocess.run(cmd, cwd=str(cwd or ROOT), capture_output=True, text=True, check=check)
```

**Good**: The code correctly avoids `shell=True`.
**Issue**: No validation of `cmd` list elements before execution.

## 🟢 LOW Priority Issues

### 10. Missing Rate Limiting
The webhook and API endpoints have no rate limiting, making them susceptible to abuse.

### 11. No CORS Configuration
The FastAPI webhook endpoint doesn't configure CORS headers.

### 12. Incomplete Error Message Sanitization
Error messages might leak system information through stack traces.

## Positive Security Features Found ✅

1. **Pydantic Validation**: Comprehensive input validation using Pydantic models
2. **No shell=True**: Subprocess calls correctly avoid shell interpretation
3. **Environment Filtering**: `get_safe_subprocess_env()` filters environment variables
4. **Command Whitelisting**: Slash commands are validated against whitelist
5. **ADW Bot Identifier**: Prevents webhook loops by identifying bot comments
6. **Token Length Limits**: Prevents DoS through oversized inputs
7. **Null Byte Protection**: Checks for null bytes in user input

## Immediate Action Items

### Before Public Release (MANDATORY):

1. **Fix scout_simple.py command injection** - Add input sanitization
2. **Implement webhook authentication** - Add GitHub signature verification
3. **Add JSON payload validation** - Prevent malformed/oversized requests
4. **Strengthen path traversal protection** - Use Path.resolve() consistently
5. **Add branch protection** - Prevent operations on main/master branches

### Recommended Security Enhancements:

1. **Security Headers**: Add CSP, X-Frame-Options, X-Content-Type-Options
2. **Rate Limiting**: Implement per-IP and per-endpoint rate limits
3. **Audit Logging**: Log all security-relevant events
4. **Secret Management**: Use proper secret management service
5. **Input Validation Tests**: Add security-focused unit tests
6. **Dependency Scanning**: Regular vulnerability scanning of dependencies

## Sample Fixes

### Webhook Authentication Fix:
```python
import hmac
import hashlib

def verify_webhook_signature(payload_body: bytes, signature_header: str, secret: str) -> bool:
    """Verify GitHub webhook signature."""
    if not signature_header:
        return False

    expected_signature = 'sha256=' + hmac.new(
        secret.encode(),
        payload_body,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected_signature, signature_header)

@app.post("/gh-webhook")
async def github_webhook(request: Request):
    # Get signature from header
    signature = request.headers.get("X-Hub-Signature-256", "")

    # Get raw payload
    payload_body = await request.body()

    # Verify signature
    webhook_secret = os.getenv("GITHUB_WEBHOOK_SECRET")
    if not webhook_secret or not verify_webhook_signature(payload_body, signature, webhook_secret):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Parse verified payload
    payload = await request.json()
```

### Path Traversal Fix:
```python
def validate_safe_path(file_path: str, base_dir: str = ".") -> str:
    """Validate file path is within allowed directory."""
    base = Path(base_dir).resolve()
    target = Path(file_path).resolve()

    try:
        target.relative_to(base)
    except ValueError:
        raise ValueError(f"Path {file_path} is outside allowed directory")

    # Check for symlinks
    if target.is_symlink():
        raise ValueError(f"Symlinks not allowed: {file_path}")

    return str(target)
```

## Conclusion

The codebase shows good security awareness with Pydantic validation and environment filtering. However, critical vulnerabilities in webhook authentication, command injection, and path traversal must be fixed before public release. The fixes are straightforward and can be implemented quickly.

**Overall Security Score**: 6/10
**Status**: NOT READY for public release
**Estimated Fix Time**: 4-6 hours for critical issues

## Verification Steps

After implementing fixes:
1. Run security tests: `pytest tests/security/`
2. Perform penetration testing on webhook endpoint
3. Validate all subprocess calls use sanitized inputs
4. Verify no secrets in logs or error messages
5. Conduct code review focusing on security changes