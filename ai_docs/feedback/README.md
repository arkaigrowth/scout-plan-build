# Feedback Loop Storage

**Purpose:** Enable continuous learning from AI predictions vs actual outcomes.

**Pattern Source:** [Agentic Engineering Primitives V2](../reference/AGENTIC_ENGINEERING_PRIMITIVES_V2.md) - Section 8

---

## Directory Structure

```
feedback/
├── README.md           ← This file
├── predictions/        ← What AI predicted/generated
├── outcomes/           ← What actually happened
└── corrections/        ← Learned patterns from errors
```

## How It Works

```
1. PREDICT: AI generates output (plan, build, estimate)
   → Save to predictions/{task_id}.json

2. OBSERVE: User reports actual outcome
   → Save to outcomes/{task_id}.json

3. LEARN: Compare prediction vs outcome
   → If error > threshold, save to corrections/{pattern}.json

4. APPLY: Next time similar input appears
   → Check corrections/ for learned patterns
```

## File Formats

### predictions/{task_id}.json
```json
{
  "task_id": "ADW-AUTH-001",
  "timestamp": "2025-11-22T10:30:00Z",
  "type": "build_estimate",
  "prediction": {
    "files_changed": 5,
    "estimated_time": "2 hours",
    "confidence": 0.8
  },
  "input_context": "JWT authentication implementation"
}
```

### outcomes/{task_id}.json
```json
{
  "task_id": "ADW-AUTH-001",
  "timestamp": "2025-11-22T14:30:00Z",
  "actual": {
    "files_changed": 8,
    "actual_time": "4 hours",
    "success": true
  },
  "error_delta": {
    "files": "+3",
    "time": "+2 hours"
  }
}
```

### corrections/{pattern}.json
```json
{
  "pattern": "auth_implementation",
  "lesson": "JWT auth typically requires 2x estimated time due to security testing",
  "correction_factor": 2.0,
  "confidence": 0.9,
  "examples": ["ADW-AUTH-001", "ADW-AUTH-003"]
}
```

## Integration Points

| Phase | Feedback Type | What to Track |
|-------|--------------|---------------|
| **Scout** | File relevance | Did we find the right files? |
| **Plan** | Estimate accuracy | Time, complexity, file count |
| **Build** | Implementation success | Tests pass? Bugs introduced? |
| **Review** | Issue detection | Did we catch problems? |

## Future Enhancements

- [ ] Automated prediction→outcome comparison
- [ ] Pattern extraction from corrections
- [ ] Integration with observability (Langfuse)
- [ ] Vector embeddings for semantic pattern matching

---

*Created: 2024-11-22*
*Pattern: V2 Feedback Loop Architecture*
