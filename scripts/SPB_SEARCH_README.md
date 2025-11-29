# SPB Search CLI Tool

A command-line interface for hybrid code search that combines semantic search (Gemini) with literal search (ripgrep).

## Installation

Install required dependencies:

```bash
pip install typer rich
```

Or add to your project dependencies:
```toml
typer = "^0.9.0"
rich = "^13.0.0"
```

## Usage

### Basic Search

```bash
# Conceptual search (automatic routing)
python scripts/spb_search.py search "how does authentication work"

# With filters
python scripts/spb_search.py search "error handling" --path src/api --lang python

# Limit results
python scripts/spb_search.py search "config" --limit 5
```

### Search Modes

```bash
# Force literal search only (ripgrep, no Gemini)
python scripts/spb_search.py search --literal "TODO: fix"

# Force semantic search only (Gemini, no ripgrep)
python scripts/spb_search.py search --semantic "billing patterns"

# Hybrid search (default - uses both)
python scripts/spb_search.py search "authentication middleware"
```

### Output Formats

```bash
# Table format (default, human-friendly)
python scripts/spb_search.py search "billing"

# JSON format (machine-readable)
python scripts/spb_search.py search "billing" --format json

# Markdown format (copy/paste friendly)
python scripts/spb_search.py search "billing" --format markdown
```

### Advanced Options

```bash
# Filter by directory
python scripts/spb_search.py search "validation" --path adws/adw_modules

# Filter by language
python scripts/spb_search.py search "class definition" --lang python

# Verbose output for debugging
python scripts/spb_search.py search "config" --verbose

# Combine filters
python scripts/spb_search.py search "api endpoint" \
  --path src/api \
  --lang python \
  --limit 20 \
  --format json
```

### Check Backend Status

```bash
python scripts/spb_search.py stats
```

## Features

### Intelligent Query Routing

The tool automatically classifies your query and routes it to the best search backend:

- **Conceptual queries** (→ Gemini only)
  - "How does billing work?"
  - "Find similar patterns to auth"
  - "Explain the payment flow"

- **Literal queries** (→ ripgrep only)
  - "TODO: fix"
  - "function calculateTotal"
  - "class UserService"

- **Hybrid queries** (→ both Gemini + ripgrep)
  - "Where is JWT validation?"
  - "Find API endpoints"
  - "authentication middleware"

### Result Merging

When using hybrid search, results from both sources are:
1. Deduplicated by file path
2. Scored and ranked (files found by both sources rank higher)
3. Merged into a unified result set

### Graceful Degradation

- If Gemini is not configured, automatically falls back to ripgrep-only
- Clear error messages if dependencies are missing
- Non-zero exit code when no results found (useful for scripting)

## Output Examples

### Table Format (Default)

```
╭─────────────────────────────────────────────────────────╮
│                    Search Results                       │
│ Query: authentication middleware                        │
│ Type: ⚡ HYBRID | Sources: gemini, ripgrep | Results: 8 │
╰─────────────────────────────────────────────────────────╯

  #  File                              Line  Source   Preview
──────────────────────────────────────────────────────────────
  1  adws/adw_modules/agent.py          45   merged   def authenticate_request...
  2  middleware/auth.py                 12   gemini   class AuthMiddleware:...
  3  tests/test_auth.py                 88   ripgrep  # Test auth flow...
```

### JSON Format

```json
{
  "query": "billing",
  "query_type": "hybrid",
  "sources_used": ["gemini", "ripgrep"],
  "total_results": 5,
  "success": true,
  "snippets": [
    {
      "file_path": "src/billing/service.py",
      "content": "class BillingService:\n    ...",
      "line_start": 12,
      "line_end": 45,
      "score": 1.3,
      "source": "merged",
      "metadata": {"sources": ["gemini", "ripgrep"]}
    }
  ]
}
```

### Markdown Format

```markdown
# Search Results: billing

- **Query Type**: hybrid
- **Sources Used**: gemini, ripgrep
- **Results Found**: 5

## Results

### 1. `src/billing/service.py:12` [merged]

\`\`\`
class BillingService:
    def process_payment(self, amount):
        ...
\`\`\`
```

## Integration with Other Tools

### Use in Shell Scripts

```bash
#!/bin/bash
# Find all TODOs in the codebase
python scripts/spb_search.py search --literal "TODO:" --format json > todos.json

# Exit code handling
if python scripts/spb_search.py search "API_KEY" --literal; then
    echo "Warning: API keys found in code!"
    exit 1
fi
```

### Pipe to Other Tools

```bash
# Get file list as JSON and process with jq
python scripts/spb_search.py search "config" --format json | jq '.snippets[].file_path'

# Format as markdown and save
python scripts/spb_search.py search "architecture" --format markdown > docs/architecture.md
```

## Requirements

### System Dependencies

- **ripgrep** (rg) - For literal search
  ```bash
  # macOS
  brew install ripgrep

  # Ubuntu/Debian
  apt-get install ripgrep
  ```

### Optional: Gemini File Search

To enable semantic search:

1. Set environment variable:
   ```bash
   export GEMINI_API_KEY="your-api-key"
   ```

2. Create a Gemini index (see main project docs)

3. Ensure state file exists at `scout_outputs/.gemini_index_state.json`

Without Gemini, the tool falls back to ripgrep-only mode.

## Error Handling

The tool provides clear error messages:

```bash
# Gemini not configured
→ Note: Gemini search unavailable, using ripgrep only

# No results found (exit code 1)
→ No results found.

# Invalid flags
→ Error: Cannot use both --literal and --semantic flags
```

## Performance Notes

- **Literal search**: Very fast (~0.1s for medium codebases)
- **Semantic search**: Moderate (~1-2s depending on Gemini API)
- **Hybrid search**: Runs both in parallel when possible

## Troubleshooting

### "Required dependencies not installed"
```bash
pip install typer rich
```

### "Gemini search not available"
```bash
# Check environment
echo $GEMINI_API_KEY

# Check index state
cat scout_outputs/.gemini_index_state.json

# Create index if needed (see main project docs)
```

### "ripgrep not installed"
```bash
# Install ripgrep
brew install ripgrep  # macOS
apt install ripgrep   # Linux
```

### No results with semantic search
Try using `--verbose` to see debug output:
```bash
python scripts/spb_search.py search "query" --semantic --verbose
```

## Development

The tool imports from `adws.adw_modules.gemini_search`:
- `HybridSearchClient` - Main search client
- `quick_search` - Quick hybrid search
- `semantic_search` - Gemini-only search
- `literal_search` - ripgrep-only search
- `QueryType` - Query classification enum

### Architecture

```
spb_search.py (CLI)
    ↓
adws/adw_modules/gemini_search.py (Backend)
    ↓
    ├── Gemini File Search API (semantic)
    └── ripgrep (literal)
```

## Future Enhancements

Potential additions:
- [ ] Interactive mode for refining queries
- [ ] Context expansion (show more lines around match)
- [ ] Exclude patterns (ignore test files, etc.)
- [ ] Config file support (~/.spb_search.toml)
- [ ] Search history and favorites
- [ ] Syntax highlighting in table output
- [ ] Export to different formats (CSV, XML)
