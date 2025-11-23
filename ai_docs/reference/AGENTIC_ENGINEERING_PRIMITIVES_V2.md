# Agentic Engineering Primitives V2 - November 2025 Edition

**Purpose:** Battle-tested engineering principles for AI-assisted development in the post-GPT-5 era

**Reality Check:** It's November 2025. Gemini 3.0 Pro just dropped. Claude Opus 4.1 codes for 7 hours straight. GPT-5 has 400K context. If you're not leveraging these capabilities, you're building with stone tools.

**Use this when:**

- Passing projects between Claude 4.1, Gemini 3.0, GPT-5, or Grok 4
- Building production AI agents that won't embarrass you
- Trying to avoid the $47,000 average cost of an AI security incident

---

## 🔥 The Brutal Truth About Modern AI Development

**Models Lie** | **Context Windows Degrade** | **Costs Explode** | **Agents Go Rogue**

If you're not prepared for these realities, you're not ready for production.

---

## 1. Single Source of Truth (SSOT) - Now With AI Memory

### The Old Way (Still Valid)

```
✅ GOOD: All user data → users/ directory
✅ GOOD: All AI outputs → outputs/ directory
```

### The 2025 Way (What Actually Works)

```
project/
├── src/               # Human code
├── outputs/           # AI artifacts (TIMESTAMPED)
│   ├── 2025-11-22/    # Daily partitions prevent 100K file directories
│   └── feedback/      # Where AI learns from its mistakes
├── memory/            # Agent state (Redis/Upstash backed)
│   ├── embeddings/    # Semantic memory (1M+ vectors)
│   └── corrections/   # User feedback loops
└── observability/     # Langfuse/Phoenix traces
```

### Real Failure Story

**Company:** FinTech startup using GPT-4
**Mistake:** No SSOT for AI outputs
**Result:** 3 different agents wrote to 3 different locations, overwrote each other's work, lost $120K in duplicate API calls before anyone noticed
**Lesson:** `outputs/{date}/{agent_id}/{task_id}/` or die

---

## 2. Right-Sizing in the Multi-Model Era

### The New Decision Matrix (November 2025)

| Task Type                 | Best Model       | Why                        | Cost Reality                     |
| ------------------------- | ---------------- | -------------------------- | -------------------------------- |
| Quick prototype           | Gemini 2.5 Flash | 2x faster than competitors | $0.30/million tokens             |
| Production coding         | Claude Opus 4.1  | 74.5% SWE-bench            | $15 input/$75 output - EXPENSIVE |
| Math/Reasoning            | Grok 4           | 100% AIME 2025             | $300/month heavy use             |
| Massive context           | Gemini 2.5 Pro   | 1M tokens actually work    | $2.50 >200K tokens               |
| Multi-agent orchestration | GPT-5 + Swarm    | Native delegation          | $2 input/$8 output               |

### Anti-Pattern: The "GPT-5 Everything" Trap

```
❌ Using GPT-5 for simple regex ($2 per million tokens for REGEX??)
❌ Using Claude Opus 4.1 for math (33.9% AIME vs Grok's 100%)
❌ Using ANY frontier model without caching (75% savings with caching)
❌ Building without fallbacks (OpenAI goes down WEEKLY)
```

### The Multi-Model Strategy (What 78% of Enterprises Do)

```python
class SmartRouter:
    def route(self, task):
        if task.is_coding and task.safety_critical:
            return claude_opus_4_1  # Best safety scores
        elif task.is_math:
            return grok_4  # Perfect math scores
        elif task.needs_massive_context:
            return gemini_2_5_pro  # 1M tokens
        elif task.is_simple:
            return gemini_flash_lite  # $0.10/million
        else:
            return gpt_5  # General purpose
```

---

## 3. The State Management Revolution

### Forget "Start Stateless" - That's 2024 Thinking

In 2025, EVERY production AI system needs state because:

1. **Gemini 3.0's bidirectional streaming** requires session management
2. **MCP (Model Context Protocol)** is now standard - requires connection state
3. **Users expect memory** - "Why doesn't it remember what I said 5 minutes ago?"

### The Modern State Stack

```python
# Level 0: In-Memory (Dev only)
state = {"messages": [], "context": {}}

# Level 1: Redis/Upstash (Production minimum)
import redis
state = redis.Redis().hgetall(f"session:{session_id}")

# Level 2: Vector + KV (RAG-enabled agents)
from qdrant_client import QdrantClient
semantic_memory = QdrantClient().search(query_vector)
operational_state = redis.get(f"state:{agent_id}")

# Level 3: Distributed + Durable (Enterprise)
# Kafka for events, PostgreSQL for state, S3 for artifacts
```

### Real Failure Story

**Company:** E-commerce platform
**Mistake:** "We'll add state later"
**Result:** Customer asked "What about the blue one?" after 3 messages. Agent had no context. Customer rage-quit. Happened 10,000 times before they noticed.
**Fix:** Implemented Redis session state, 40% increase in completion rate

---

## 4. The Multimodal Output Pattern

### It's Not Just Text Anymore

Gemini 2.0 Flash now supports multimodal output like natively generated images mixed with text and steerable text-to-speech multilingual audio. If you're not structuring for this, you're behind.

```
outputs/
├── text/              # Traditional
├── images/            # Gemini 2.0 native generation
├── audio/             # 11Labs, Gemini TTS
├── video/             # Coming Q1 2026
└── composite/         # Mixed media responses
    └── response_123/
        ├── main.md
        ├── diagram.png    # Generated inline
        └── narration.mp3  # TTS of main content
```

---

## 5. Framework Selection in 2025

### The Brutal Truth About Frameworks

| Framework                     | When to Use            | When to Avoid     | Hidden Cost                         |
| ----------------------------- | ---------------------- | ----------------- | ----------------------------------- |
| **LangChain/LangGraph** | Complex DAG workflows  | Simple tasks      | Steep learning curve, 1000+ classes |
| **OpenAI Agents SDK**   | Multi-agent delegation | Non-OpenAI models | Vendor lock-in                      |
| **Google ADK**          | Gemini optimization    | Cross-model needs | Beta instability                    |
| **CrewAI**              | Role-based agents      | Single agent      | Coordination overhead               |
| **LlamaIndex**          | RAG-heavy apps         | Simple Q&A        | Memory overhead                     |
| **DSPy**                | Prompt optimization    | Quick prototypes  | Complexity explosion                |
| **Vercel AI SDK**       | Next.js apps           | Python backends   | TypeScript only                     |

### The "Use What Works" Pattern

```typescript
// Frontend: Vercel AI SDK (it's unbeatable for Next.js)
import { generateText } from '@ai-sdk/google';

// Orchestration: LangGraph (when you need control)
from langgraph import StateGraph

// Memory: LlamaIndex (best-in-class retrieval)
from llama_index import VectorStoreIndex

// Observability: Langfuse (open-source, reliable)
from langfuse import Langfuse
```

---

## 6. The 2025 Security Reality

### New Attack Vectors

Independent security researchers conducted comprehensive prompt injection tests showing Claude Opus 4.1 had 4.1% successful attacks while Gemini Deep Think performed weaker at 14.6%

```python
# MANDATORY Security Layers

# 1. Input Sanitization (Now handles multimodal)
def sanitize_multimodal(input_data):
    if input_data.type == "image":
        check_for_adversarial_pixels()
    if input_data.type == "text":
        check_for_prompt_injection()
  
# 2. Output Validation (LLMs hallucinate prices)
def validate_pricing(ai_output):
    if ai_output.price > historical_max * 2:
        flag_for_review()
  
# 3. Cost Controls (CRITICAL in 2025)
class CostLimiter:
    def __init__(self):
        self.daily_limit = 1000  # dollars
        self.per_user_limit = 10
        self.model_budgets = {
            "claude_opus": 100,  # It's expensive
            "gpt_5": 500,
            "gemini_flash": 400
        }
```

### Real Security Incident

**Company:** Legal firm
**Attack:** Adversarial document uploaded
**Result:** Agent leaked client data to public response
**Cost:** $2.3M settlement + reputation
**Fix:** Implemented Guardrails + NeMo security layer

---

## 7. Observability Is Not Optional

### The Modern Observability Stack

```python
# Bare Minimum (You'll regret not having this)
from langfuse import Langfuse
langfuse = Langfuse()

@langfuse.trace
def my_agent_task():
    # Every LLM call is now traced
    pass

# Production Grade
class ObservabilityStack:
    def __init__(self):
        self.traces = Langfuse()  # Open-source
        self.metrics = Phoenix()   # Drift detection
        self.costs = Helicone()    # Cost tracking
        self.security = Guardrails() # Safety
```

### What to Track in 2025

- **Latency per model** (Gemini Flash is 2x faster than GPT-5)
- **Token usage per user** (One user spent $5,000 in a day)
- **Drift detection** (Model behavior changes without warning)
- **Tool usage patterns** (Which agents use which tools)
- **Failure cascades** (One timeout can break everything)

---

## 8. The Feedback Loop Architecture

### This Is How You Get From 60% to 90% Accuracy

```python
class FeedbackLoop:
    def __init__(self):
        self.predictions = []
        self.outcomes = []
        self.corrections = {}
  
    def record_prediction(self, input, output, confidence):
        prediction_id = uuid4()
        self.predictions.append({
            "id": prediction_id,
            "input": input,
            "output": output,
            "confidence": confidence,
            "timestamp": datetime.now()
        })
        return prediction_id
  
    def record_outcome(self, prediction_id, actual_outcome):
        # This is where learning happens
        prediction = self.get_prediction(prediction_id)
        error = calculate_error(prediction.output, actual_outcome)
      
        if error > threshold:
            self.corrections[prediction.input_pattern] = {
                "expected": actual_outcome,
                "got": prediction.output,
                "lesson": generate_lesson(error)
            }
  
    def apply_learning(self, new_input):
        # Check if we've seen this pattern before
        if pattern_match(new_input, self.corrections):
            return self.corrections[pattern].expected
```

### Real Success Story

**Company:** Liquidate.ai (garage sale pricing)
**Initial Accuracy:** 61% pricing within 20% of sale price
**After Feedback Loops:** 89% accuracy
**Key:** Every sale feeds back actual price vs prediction

---

## 9. The Cost Management Imperative

### November 2025 Pricing Reality

| Model           | Input$/M | Output $/M | Hidden Costs        |                  |
| --------------- | ----------------------- | ------------------- | ---------------- |
| Claude Opus 4.1 | $15 | $75               | No caching discount |                  |
| GPT-5           | $2 | $8                 | 75% cache discount  |                  |
| Gemini 2.5 Pro  | $1.25-$2.50             | $10-$15             | Increases >200K  |
| Grok 4          | Subscription            | Model               | $300/month heavy |
| Gemini Flash    | $0.30 | $1.20           | Best value          |                  |

### The Smart Cost Strategy

```python
class CostOptimizer:
    def __init__(self):
        self.cache = {}  # 75% savings on GPT-5
        self.router = SmartRouter()
      
    def process(self, request):
        # 1. Check cache first
        if cached := self.cache.get(request.hash):
            return cached  # $0 cost
      
        # 2. Try cheap model first
        if request.complexity < 3:
            result = gemini_flash.process(request)  # $0.30/M
            if result.confidence > 0.8:
                return result
      
        # 3. Escalate only if needed
        return self.router.route_to_expensive_model(request)
```

---

## 10. The MCP (Model Context Protocol) Revolution

### Every Agent Needs MCP in 2025

MCP is now the standard for tool integration. Model Context Protocol (MCP) has become the de facto standard for integrating systems and applications with LLMs, with support now available across major AI platforms.

```python
# Before MCP (Old way, fragile)
def my_agent():
    if need_database:
        custom_db_integration()
    if need_search:
        custom_search_integration()
    # 50 custom integrations...

# With MCP (Standard, beautiful)
from mcp import MCPServer

class MyAgent:
    def __init__(self):
        self.mcp = MCPServer()
        self.mcp.connect("clickhouse://...")  # Instant DB access
        self.mcp.connect("github://...")      # Instant GitHub
        self.mcp.connect("slack://...")       # Instant Slack
        # Any MCP server just works
```

---

## 11. The Gemini Superpower Most People Miss

### Native Multimodal Processing at Scale

Gemini 2.5 Flash is best for large scale processing, low-latency, high volume tasks that require thinking, and agentic use cases

```python
# What everyone does (slow, expensive)
for image in images:
    result = analyze_image(image)  # 1000 API calls

# What you should do with Gemini
results = gemini.analyze_batch(
    images[:1000],  # Send ALL at once
    "Group these by visual similarity and extract prices"
)
# 1 API call, 100x faster, 10x cheaper
```

---

## 12. The Testing Reality Check

### You Can't Test LLMs Like Traditional Code

```python
# ❌ This will fail randomly
def test_ai_response():
    assert ai.generate("Hello") == "Hi there!"  # Non-deterministic

# ✅ Test structure, not content
def test_ai_response_structure():
    response = ai.generate("Price this item")
    assert "price" in response
    assert "confidence" in response
    assert 0 <= response["confidence"] <= 1
    assert response["price"] > 0
```

### The Evaluation Framework You Actually Need

```python
class LLMEvaluator:
    def __init__(self):
        self.metrics = {
            "structure": self.check_schema,
            "safety": self.check_guardrails,
            "cost": self.check_token_usage,
            "latency": self.check_response_time,
            "drift": self.check_embedding_stability
        }
  
    def evaluate_in_production(self):
        # Sample 1% of production traffic
        # Check against baseline
        # Alert on degradation
        pass
```

---

## 13. The Deployment Pattern That Actually Works

### Not Everything Needs Kubernetes

```yaml
# For <1000 requests/day: Vercel + Edge Functions
# Simple, cheap, fast
vercel:
  functions:
    api/agent.ts:
      maxDuration: 300  # 5 minutes for Opus 4.1 thinking

# For >10K requests/day: Container + Horizontal Scale
docker-compose:
  agent:
    image: agent:latest
    scale: 5
    environment:
      - REDIS_URL
      - MODEL_ROUTER_URL

# For >100K requests/day: Now you need k8s
# But not before
```

---

## 14. The "Build vs Buy" Decision Matrix

### When to Build Your Own

- Core business logic
- Unique competitive advantage
- Need full control
- Have AI expertise in-house

### When to Buy/Use Existing

- Observability → Langfuse
- Vector DB → Qdrant/Pinecone
- Orchestration → LangGraph
- Fine-tuning → OpenAI/Vertex AI

### When to Hybrid

- Use Vercel AI SDK + custom business logic
- LlamaIndex for RAG + custom agents
- MCP for integrations + custom tools

---

## Quick Reference: November 2025 Best Practices

### Starting a New AI Project

1. **Pick your models** (plural - you need 2-3 minimum)
2. **Set up observability FIRST** (Langfuse minimum)
3. **Implement cost controls** (before you deploy)
4. **Design for multimodal** (even if starting text-only)
5. **Build feedback loops** (from day 1)
6. **Use MCP for integrations** (don't build custom)
7. **Cache aggressively** (75% cost savings)
8. **Test structure, not content** (LLMs are not deterministic)
9. **Deploy simple first** (Vercel, not k8s)
10. **Monitor drift** (models change behavior)

### The One Metric That Matters

**Time to User Value** - Everything else is vanity

If your AI agent isn't providing value in <10 seconds for 80% of requests, you're over-engineering.

---

## Model-Agnostic Prompt for Cross-Model Work

```
Context: Building [PROJECT_NAME] using November 2025 AI capabilities

Available Models:
- Claude Opus 4.1: Best for coding (74.5% SWE-bench)
- Gemini 3.0 Pro: Best for multimodal and scale (1M context)
- GPT-5: Best for general reasoning (400K context)
- Grok 4: Best for math (100% AIME)

Current Stack:
- Framework: [LangGraph/CrewAI/etc]
- State: [Redis/PostgreSQL]
- Observability: [Langfuse/Phoenix]
- Deployment: [Vercel/AWS/GCP]

Task: [What you need]

Requirements:
1. Use model-appropriate patterns
2. Implement cost controls
3. Include feedback loops
4. Design for multimodal
5. Follow MCP standards
```

---

*Last Updated: November 22, 2025*
*Written by someone who learned these lessons the hard way*
*$2.3M in AI mistakes taught us these patterns*
