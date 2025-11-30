
## mem0 Deep Dive (2025-11-29)

### Article to Process
- URL: https://dev.to/yigit-konur/mem0-the-comprehensive-guide-to-building-ai-with-persistent-memory-fbm
- **Quick method**: Copy/paste from browser → save to `ai_docs/research/articles/mem0-comprehensive-guide.md`
- Then run: `python scripts/research-add.py analyze <file>` → `create '<json>'`

### Future Enhancement: URL Support for research-add.py
- Add URL fetching capability using Gemini URL context (1M tokens, cheap)
- Or use Claude's WebFetch as fallback
- Makes adding web articles one-liner: `research-add.py add-url <url>`

### Investigation Topics
1. Metadata schema best practices (from article)
2. API patterns (not MCP) for secure integration
3. Wire mem0 into Plan/Build phases (not just Scout)
4. Memory lifecycle management (expiration, consolidation)

### Current State
- ✅ mem0 cloud connected (project: data_refinery, proj_id in .env)
- ✅ Scout integration working (records discoveries, gets hints)
- ✅ spb search CLI working
- ⏳ Plan/Build phases need wiring
- ⏳ Metadata schema needs design from article
