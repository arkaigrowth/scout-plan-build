# Mem0 Direct API/SDK Usage Research

**Date:** 2025-11-29  
**Status:** Comprehensive Research Complete  
**Scope:** Direct Python SDK usage (non-MCP)

---

## Executive Summary

Mem0 is a universal memory layer for AI agents that provides both a managed cloud platform and self-hosted open-source solution. The **`mem0ai` Python package** (v1.0.1+) enables direct SDK integration without MCP servers. Two distinct client patterns exist: `Memory` for self-hosted/local usage and `MemoryClient` for the cloud platform. Authentication via API key is straightforward, featuring semantic search with metadata filtering, and pricing scales from free (10K memories) to enterprise. For your indexer use case, self-hosted `Memory` offers maximum flexibility; cloud `MemoryClient` provides managed infrastructure if you need it.

---

## Installation & Setup

### Package Information

| Property | Details |
|----------|---------|
| **Package Name** | `mem0ai` |
| **Current Version** | 1.0.1+ |
| **PyPI URL** | https://pypi.org/project/mem0ai/ |
| **Repository** | https://github.com/mem0ai/mem0 |

### Installation

```bash
# Install the core SDK
pip install mem0ai

# For development with latest features
pip install mem0ai[dev]

# Specific version
pip install mem0ai==1.0.1
```

### Minimal Dependencies
- Python 3.10+
- OpenAI API key (for default LLM, optional if using alternative)
- Qdrant (vector database, included by default locally)

---

## Authentication Patterns

### Pattern 1: Self-Hosted (Memory Class)

For local/self-hosted usage, no authentication required:

```python
from mem0 import Memory

# Initialize with defaults (OpenAI GPT-4 for LLM, Qdrant for vectors)
memory = Memory()

# Or configure custom settings
config = {
    "llm": {
        "provider": "openai",
        "config": {
            "model": "gpt-4-turbo",
            "api_key": "your-openai-key"
        }
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": "memories",
            "path": "/tmp/qdrant"  # Local disk storage
        }
    },
    "version": "v1.1"
}

memory = Memory.from_config(config)
```

### Pattern 2: Cloud Platform (MemoryClient)

For managed Mem0 Platform:

```python
import os
from mem0 import MemoryClient

# Set API key from environment or directly
api_key = os.getenv("MEM0_API_KEY", "your-api-key-here")

# Initialize cloud client
client = MemoryClient(api_key=api_key)
```

**API Key Management:**
- Obtain from: https://app.mem0.ai → Settings → API Keys
- Format: `Token <api-key>` (handled automatically by SDK)
- Store in environment: `export MEM0_API_KEY="your-key"`
- Use in code: `os.environ["MEM0_API_KEY"] = "your-api-key"`

---

## Core API Examples

### Memory Class (Self-Hosted/Local)

#### 1. Add a Memory

```python
from mem0 import Memory

memory = Memory()

# Basic add with user context
messages = [
    {"role": "user", "content": "I'm Alex, a Python developer who loves open-source"},
    {"role": "assistant", "content": "Got it! I'll remember you're a Python dev in open-source."}
]
result = memory.add(messages, user_id="alex_001")

# With metadata for better organization
memory.add(
    "I prefer window seats on flights and bring noise-canceling headphones",
    user_id="alex_001",
    metadata={
        "category": "travel_preferences",
        "importance": "medium",
        "source": "user_interview"
    }
)

print(result)
# Output: {'message_ids': ['mem_abc123'], 'added': [...]}
```

#### 2. Search Memories

```python
# Simple semantic search
results = memory.search(
    "What are my travel preferences?",
    user_id="alex_001"
)

print(results)
# Output:
# {
#   "results": [
#     {
#       "id": "mem_abc123",
#       "memory": "Prefers window seats on flights, brings noise-canceling headphones",
#       "user_id": "alex_001",
#       "score": 0.89,
#       "created_at": "2025-10-22T04:40:22.864647-07:00",
#       "updated_at": "2025-10-22T04:40:22.864647-07:00"
#     }
#   ]
# }

# Search with filter
results = memory.search(
    "programming interests",
    filters={"user_id": "alex_001"}
)
```

#### 3. Update Memory

```python
# LLM-based updates (Mem0 decides when to update)
memory.add(
    [
        {"role": "user", "content": "Actually, I prefer aisle seats now"},
        {"role": "assistant", "content": "Updated your preference"}
    ],
    user_id="alex_001"
)
# Mem0 intelligently deduplicates and updates existing memories
```

#### 4. Delete Memory

```python
# Delete by specific memory ID
memory.delete(memory_id="mem_abc123")

# Delete all memories for a user (requires filter)
# Note: Use with caution
memory.delete(filters={"user_id": "alex_001"})

# Reset all memories
memory.reset()
```

#### 5. Get All Memories

```python
all_memories = memory.get_all(user_id="alex_001")

for mem in all_memories:
    print(f"- {mem['memory']} (score: {mem.get('score', 'N/A')})")
```

### MemoryClient (Cloud Platform)

#### 1. Add a Memory

```python
from mem0 import MemoryClient

client = MemoryClient(api_key="your-api-key")

# Add memory via messages
messages = [
    {"role": "user", "content": "I'm vegetarian and allergic to nuts"},
    {"role": "assistant", "content": "Got it! I'll remember your dietary restrictions."}
]
response = client.add(messages, user_id="user123")

# Direct string add
client.add(
    "Favorite color is blue, works in tech",
    user_id="user123"
)

print(response)
```

#### 2. Search with Advanced Filters

```python
# Basic search
results = client.search(
    "What are my dietary restrictions?",
    filters={"user_id": "user123"}
)

# Advanced v2 filtering with logical operators
results = client.search(
    "recent preferences",
    filters={
        "AND": [
            {"user_id": "user123"},
            {"categories": {"contains": "food"}},
            {"created_at": {"gte": "2024-07-01"}}
        ]
    }
)

# Filter by agent session
results = client.search(
    "context from chatbot",
    filters={
        "AND": [
            {"user_id": "user123"},
            {"agent_id": "chatbot_v1"},
            {"run_id": "session-123"}
        ]
    }
)
```

#### 3. Batch Operations

```python
# Add multiple memories in batch
memories_to_add = [
    "I like coffee in the morning",
    "Prefer remote work",
    "Team meeting every Monday 10am"
]

for memory_text in memories_to_add:
    client.add(memory_text, user_id="user123")
```

---

## Cloud vs Self-Hosted Comparison

| Feature | Mem0 Cloud Platform | Self-Hosted (OSS) |
|---------|-------------------|-------------------|
| **Authentication** | API key required | None required |
| **Setup Complexity** | Minimal (2 lines) | More configuration |
| **Data Ownership** | Mem0 hosted | You control |
| **Vector DB** | Managed by Mem0 | Choose: Qdrant, Milvus, Pinecone, etc. |
| **LLM Integration** | Use Mem0's configured LLM | Full flexibility (OpenAI, Anthropic, Ollama, etc.) |
| **Scalability** | Horizontal (managed) | Depends on your infrastructure |
| **Compliance** | SOC 2, HIPAA available | You manage |
| **Rate Limits** | Platform limits apply | None (depends on your LLM) |
| **Pricing** | Freemium ($0-$2000+/month) | Infrastructure costs only |
| **Ideal For** | Quick deployment, managed ops | Control, customization, self-hosting |

---

## Pricing & Limits

### Mem0 Cloud Platform Tiers

| Tier | Cost | Memories | Use Case |
|------|------|----------|----------|
| **Free** | $0/month | 10,000 | Development, testing |
| **Starter** | $19/month | Paid per operation | Small projects, growing teams |
| **Pro** | $249/month | Unlimited | Teams with advanced needs |
| **Enterprise** | $2,000+/month | Unlimited + SLA | Large orgs, compliance needs |

**Pricing Model:** Usage-based billing tied to memory operations (add, search, update, delete), not per-seat.

### Rate Limits

**Cloud Platform:**
- Not explicitly documented in public docs
- Pro and Enterprise plans likely have higher limits
- Recommended: Contact sales for your use case

**Self-Hosted (OSS):**
- No platform-imposed rate limits
- Limited by your LLM provider's rate limits
- Unlimited local vector store operations

### Startup Program

Free 3 months of Pro plan + priority support for startups with <$5M funding.

---

## Advanced Features

### Semantic Search + Metadata Filtering

```python
from mem0 import Memory

memory = Memory()

# Store memories with rich metadata
memory.add(
    "I have a linear algebra midterm exam on November 20",
    user_id="student_001",
    metadata={
        "category": "academic",
        "type": "exam",
        "subject": "math",
        "date": "2025-11-20"
    }
)

# Semantic search with category filter (Platform only)
results = memory.search(
    "upcoming exams",
    filters={
        "AND": [
            {"user_id": "student_001"},
            {"categories": {"contains": "academic"}}
        ]
    }
)

# Self-hosted: simpler filtering
results = memory.search(
    "math exams",
    user_id="student_001"
)
```

### Memory History & Tracking

```python
# Get history of a specific memory
history = memory.history(memory_id="mem_abc123")

for event in history:
    print(f"{event['event_type']}: {event['old_memory']} -> {event['new_memory']}")
```

### Custom Configuration for Indexing

```python
from mem0 import Memory

# Optimized config for high-volume indexing
config = {
    "llm": {
        "provider": "openai",
        "config": {
            "model": "gpt-4-turbo",
            "api_key": os.getenv("OPENAI_API_KEY"),
            "temperature": 0.3  # Lower temp for consistency
        }
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": "indexer_memories",
            "path": "./data/vector_store",
            "batch_size": 100  # Optimize for bulk operations
        }
    },
    "version": "v1.1"
}

indexer_memory = Memory.from_config(config)

# Now use for high-volume indexing
documents = [...]  # Your documents
for doc in documents:
    indexer_memory.add(doc, user_id="indexer")
```

---

## Recommendations for Your Use Case

### For Scout/Index Operations

**Recommendation: Use Self-Hosted `Memory`**

```python
from mem0 import Memory

# Initialize once at startup
memory = Memory()

# During indexing operations
for item in items_to_index:
    memory.add(
        f"Item: {item['title']}\nDescription: {item['desc']}",
        user_id="indexer_bot",
        metadata={
            "source": "scout",
            "item_type": item['type'],
            "timestamp": item['timestamp']
        }
    )

# Later: semantic search across indexed items
search_results = memory.search(
    "Find items related to authentication",
    user_id="indexer_bot"
)
```

**Pros:**
- No API keys or network latency
- Full control over LLM (can use Anthropic API)
- Ideal for batch indexing operations
- Data stays local

**Cons:**
- Need to manage vector database
- Requires LLM API key setup
- More initial configuration

### For Cross-Session Memory

**Recommendation: Consider Cloud `MemoryClient` for multi-session contexts**

```python
# Store session-specific memories
client = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))

# After session completes
client.add(
    f"Session {session_id}: User performed {action}",
    user_id=user_id,
    metadata={"session_id": session_id, "timestamp": now}
)

# Later: retrieve context from specific session
context = client.search(
    "What did the user ask last session?",
    filters={
        "AND": [
            {"user_id": user_id},
            {"session_id": session_id}
        ]
    }
)
```

### Performance Considerations

1. **Batch Operations:** Use loops with `.add()` rather than REST API calls
2. **Vector DB:** Qdrant locally is fast; Milvus for enterprise scale
3. **LLM Calls:** Mem0 calls LLM for deduplication—batch adds for efficiency
4. **Metadata:** Lean metadata design for faster filtering

---

## Troubleshooting & Common Issues

### Issue: OpenAI API Key Not Found
```python
# Fix: Set environment variable
import os
os.environ["OPENAI_API_KEY"] = "sk-..."

# Or configure explicitly
config = {
    "llm": {
        "provider": "openai",
        "config": {"api_key": "sk-..."}
    }
}
memory = Memory.from_config(config)
```

### Issue: Qdrant Connection Error
```python
# Ensure Qdrant path exists
from pathlib import Path
Path("/tmp/qdrant").mkdir(parents=True, exist_ok=True)

memory = Memory()  # Now works
```

### Issue: Cloud API Rate Limiting
```python
import time
from mem0 import MemoryClient

client = MemoryClient(api_key=key)

# Add exponential backoff
for item in items:
    try:
        client.add(item, user_id=user_id)
    except Exception as e:
        if "rate" in str(e).lower():
            time.sleep(2)  # Wait and retry
            client.add(item, user_id=user_id)
```

---

## References & Resources

- [Mem0 Python SDK Quickstart](https://docs.mem0.ai/open-source/python-quickstart)
- [Mem0 Platform Quickstart](https://docs.mem0.ai/platform/quickstart)
- [Mem0 Search Documentation](https://docs.mem0.ai/core-concepts/memory-operations/search)
- [Mem0 GitHub Repository](https://github.com/mem0ai/mem0)
- [Mem0 PyPI Package](https://pypi.org/project/mem0ai/)
- [Mem0 Pricing](https://mem0.ai/pricing)

---

## Quick Start Template for Indexer

```python
"""
mem0 integration template for scout_plan_build_mvp indexer
"""

import os
from mem0 import Memory

class IndexerMemory:
    def __init__(self, user_id: str = "indexer"):
        """Initialize memory for indexing operations"""
        self.user_id = user_id
        self.memory = Memory()
    
    def index_items(self, items: list, source: str = "scout"):
        """Batch index items into memory"""
        for item in items:
            self.memory.add(
                f"Title: {item.get('title')}\nContent: {item.get('content')}",
                user_id=self.user_id,
                metadata={
                    "source": source,
                    "item_id": item.get('id'),
                    "timestamp": item.get('timestamp')
                }
            )
    
    def search_indexed(self, query: str, limit: int = 5) -> list:
        """Semantic search across indexed items"""
        results = self.memory.search(query, user_id=self.user_id, limit=limit)
        return results.get("results", [])
    
    def get_all(self) -> list:
        """Retrieve all indexed memories"""
        return self.memory.get_all(user_id=self.user_id)


# Usage
if __name__ == "__main__":
    indexer = IndexerMemory(user_id="scout_indexer")
    
    # Index documents
    docs = [
        {"id": 1, "title": "Authentication", "content": "How to implement JWT..."},
        {"id": 2, "title": "Database Design", "content": "SQL vs NoSQL..."}
    ]
    indexer.index_items(docs)
    
    # Search
    results = indexer.search_indexed("security and tokens")
    for result in results:
        print(f"- {result['memory']} (score: {result['score']})")
```

---

**End of Research**

*This research document provides everything needed to integrate mem0 directly into Python scripts without MCP servers. Choose self-hosted `Memory` for your indexer for maximum control and no external dependencies.*
