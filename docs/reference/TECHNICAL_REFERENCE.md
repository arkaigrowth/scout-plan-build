# Technical Reference

**Architecture, configuration, and troubleshooting for the Catsy development accelerator.**

## Architecture Overview

```
┌─────────────────┐
│  Your Request   │
└────────┬────────┘
         ↓
┌─────────────────┐
│  Scout Phase    │ → Finds relevant files
└────────┬────────┘
         ↓
┌─────────────────┐
│  Plan Phase     │ → Creates specification
└────────┬────────┘
         ↓
┌─────────────────┐
│  Build Phase    │ → Generates code
└────────┬────────┘
         ↓
┌─────────────────┐
│  Review Phase   │ → Quality checks
└────────┬────────┘
         ↓
┌─────────────────┐
│  Your Review    │
└─────────────────┘
```

## Configuration

### Required Environment Variables

```bash
# Anthropic API (Required)
export ANTHROPIC_API_KEY="sk-ant-api..."

# GitHub (Required for full workflow)
export GITHUB_REPO_URL="https://github.com/catsy/main"
export GITHUB_PAT="ghp_..."  # Optional but recommended

# Performance Tuning
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768  # Prevents truncation
```

### Optional Configuration

```bash
# R2 Storage (for artifacts)
export R2_ENDPOINT_URL="https://..."
export R2_ACCESS_KEY_ID="..."
export R2_SECRET_ACCESS_KEY="..."

# Custom Model Selection
export ADW_MODEL="claude-3-sonnet"  # or claude-3-opus
```

## Core Commands

### /plan_w_docs

Creates implementation specifications.

```bash
/plan_w_docs "[task]" "[documentation_url]" "[relevant_files]"
```

**Parameters**:
- `task`: Natural language description
- `documentation_url`: Reference docs (optional)
- `relevant_files`: JSON file with code context (optional)

**Output**: `specs/issue-NNN-adw-XXX-slug.md`

### /build_adw

Builds implementation from specification.

```bash
/build_adw "specs/[spec-file].md"
```

**Output**: Generated code files + build report

### /scout (Deprecated)

Find relevant files for a task.

```bash
/scout "[task]" "[depth]"
```

**Note**: Currently broken with external tools. Use manual file discovery instead.

## Troubleshooting

### Common Issues

#### 1. Token Limit Errors

**Error**: "Maximum token limit exceeded"

**Solution**:
```bash
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768
```

#### 2. Scout Commands Fail

**Error**: "gemini/opencode/codex not found"

**Solution**: These external tools don't exist. Use direct file paths:
```bash
/plan_w_docs "task" "docs" "agents/scout_files/relevant_files.json"
```

#### 3. Git Operations on Main

**Error**: "Cannot commit to main branch"

**Solution**: Always create feature branch first:
```bash
git checkout -b feature/issue-123
```

#### 4. Spec Validation Failures

**Error**: "Invalid specification format"

**Solution**: Ensure spec follows schema v1.1.0:
- Required sections: Overview, Technical, Task List
- YAML frontmatter with metadata
- Proper acceptance criteria

## File Structure

```
scout_plan_build_mvp/
├── adws/                    # Core workflow modules
│   ├── adw_*.py            # Workflow scripts
│   └── adw_modules/        # Shared modules
├── agents/
│   └── scout_files/        # Scout output location
├── specs/                   # Generated specifications
├── ai_docs/                # AI-generated documentation
├── tests/                   # Test suite
└── .claude/
    └── commands/           # Slash command definitions
```

## Workflow Modules

### State Management

Location: `adws/adw_modules/state.py`

Manages workflow state across executions:
```python
state = State(namespace="workflow-123")
state.save("phase", "building")
state.checkpoint("after-planning")
```

### Validation

Location: `adws/adw_modules/validators.py`

Security-first input validation:
- Path traversal prevention
- Command injection prevention
- SQL injection prevention

### Error Handling

Location: `adws/adw_modules/exceptions.py`

Structured exception hierarchy:
- `ADWError`: Base exception
- `ValidationError`: Input validation failures
- `GitHubError`: GitHub API issues
- `StateError`: State management problems

## Performance Optimization

### Caching Strategy

Scout results are cached in:
```
agents/scout_files/
└── relevant_files.json  # Reused across runs
```

### Parallel Execution (Future)

Planned architecture for parallel phases:
```python
# Coming in v2.0
parallel_tasks = [
    ("scout", scout_task),
    ("analyze", analyze_task),
    ("prepare", prepare_task)
]
execute_parallel(parallel_tasks)
```

## Security Considerations

### Input Validation

All inputs validated against:
- Allowed path prefixes
- Whitelisted commands
- Sanitized commit messages

### Secrets Management

Never commit:
- API keys
- Personal access tokens
- Database credentials

Use environment variables instead.

## API Rate Limits

### Anthropic Claude
- 1000 requests/minute
- 100,000 tokens/minute
- Automatic retry with backoff

### GitHub
- 5000 requests/hour (authenticated)
- 60 requests/hour (unauthenticated)

## Debugging

### Enable Debug Logging

```bash
export ADW_DEBUG=true
export ADW_LOG_LEVEL=DEBUG
```

### Check Execution Logs

```bash
tail -f logs/execution.log
tail -f logs/[session-id]/workflow.log
```

### Validate Specifications

```python
python -m adw_modules.spec_validator specs/my-spec.md
```

## Integration Points

### CI/CD Pipeline

```yaml
# .github/workflows/adw.yml
name: ADW Workflow
on:
  issue:
    types: [opened, edited]
jobs:
  process:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: ./adw_trigger.sh ${{ github.event.issue.number }}
```

### Webhook Integration

```python
# webhook_handler.py
@app.route('/webhook/github', methods=['POST'])
def handle_github_webhook():
    event = request.headers.get('X-GitHub-Event')
    if event == 'issues':
        trigger_adw_workflow(request.json)
```

## Monitoring

### Key Metrics

Track these for health monitoring:
- Workflow success rate (target: >90%)
- Average execution time (target: <5 min)
- Error rate by phase
- Token usage per workflow

### Health Check Endpoint

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": 3600,
  "workflows_processed": 42
}
```

## Maintenance

### Daily
- Check error logs
- Monitor token usage

### Weekly
- Clear old scout cache
- Archive completed workflows
- Update documentation

### Monthly
- Review performance metrics
- Update context files
- Refine prompts

## Version History

- **v1.0.0** - Initial MVP
- **v1.1.0** - Added spec validation
- **v1.2.0** - Improved error handling
- **v2.0.0** - (Planned) Parallel execution

## Support

**Internal Slack**: #dev-automation
**Documentation**: This file
**Issues**: GitHub Issues
**Owner**: Platform Team

---

*Last updated: 2025-01-20*