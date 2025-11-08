# TRUE MVP Implementation Plan (1 Week)

## Reality Check
**Goal**: Working, deterministic Scout→Plan→Build in 5 days
**Not Goal**: Production-ready distributed system with observability

## The Brutal Truth
- You have 1 user (yourself)
- You need it working THIS WEEK
- Perfect is the enemy of done
- Every line of code is a liability

---

## Week 1 Schedule (40 hours total)

### Day 1 (Monday) - Scout Determinism (4 hours)
**Morning (2 hours)**
- Copy existing scout logic
- Add one line: `sorted(files)`
- Test it works twice the same

**Afternoon (2 hours)**
- Integration test with existing plan phase
- Fix any breakage
- Commit and ship

**Deliverable**: Scout that returns same files in same order

### Day 2 (Tuesday) - Input Validation (4 hours)
**Morning (2 hours)**
- Wrap existing `validators.py` as a skill
- Don't change the logic, just wrap it

**Afternoon (2 hours)**
- Add to scout pipeline
- Test with malicious inputs
- Ship

**Deliverable**: Inputs validated before scout

### Day 3 (Wednesday) - State Management (6 hours)
**All Day**
- JSON file save/load (no Redis, no SQLite)
- Simple checkpoint: `json.dump(state, open('checkpoint.json', 'w'))`
- Recovery: `json.load(open('checkpoint.json'))` with try/except
- Test checkpoint/restore works

**Deliverable**: Can resume from checkpoint

### Day 4 (Thursday) - Error Handling (6 hours)
**All Day**
- Wrap everything in try/except
- Retry 3 times with exponential backoff
- Return valid empty structure on total failure
- Log errors to file

**Deliverable**: Nothing crashes, always returns something

### Day 5 (Friday) - Integration & Polish (6 hours)
**Morning (3 hours)**
- Full pipeline test: Scout→Plan→Build
- Fix integration issues
- Document how to run it

**Afternoon (3 hours)**
- Create 5 test cases
- Run them, fix failures
- Ship MVP

**Deliverable**: Working end-to-end pipeline

---

## What We're NOT Building (Yet)

### Not This Week
- ❌ Skill composition architecture
- ❌ Property-based testing
- ❌ Cross-platform determinism
- ❌ Performance monitoring
- ❌ Distributed tracing
- ❌ A/B testing framework
- ❌ Cryptographic fingerprinting
- ❌ Multiple state backends
- ❌ Complex error recovery strategies
- ❌ Workflow orchestration abstractions

### Scaffolding Only (TODOs in code)
```python
class MVPImplementation:
    def __init__(self):
        # MVP: Just these
        self.state = {}

        # TODO (Month 1): Add when needed
        self.cache = None  # When slow
        self.metrics = None  # When debugging sucks
        self.advanced_retry = None  # When simple retry isn't enough
```

---

## The 3 Skills We Actually Need

### 1. skill-000-mvp: Scout Determinism (50 lines)
```python
def scout(task):
    files = find_files(task)
    return sorted(files)  # THE FIX
```

### 2. skill-002-mvp: Input Validation (Reuse existing)
```python
def validate(input):
    return existing_validators.validate(input)  # Just wrap it
```

### 3. skill-003-mvp: State Management (30 lines)
```python
def save_state(state):
    json.dump(state, open('state.json', 'w'))

def load_state():
    try:
        return json.load(open('state.json'))
    except:
        return {}
```

---

## Success Metrics (MVP)

| Metric | Target | Why |
|--------|--------|-----|
| Works? | Yes | That's the point |
| Deterministic? | Same output twice | Minimum viable |
| Fast enough? | <2 minutes | You can wait that long |
| Doesn't crash? | Returns something | Good enough |
| Test coverage? | 5 manual tests | You're the user |

---

## Month 1 Expansion (Only if needed)

After MVP is working and you've used it for a month:

### Actual Pain Points to Address
1. **IF too slow** → Add caching
2. **IF debugging sucks** → Add logging
3. **IF state gets corrupted** → Add backup
4. **IF you need multiple workflows** → Add orchestration

### NOT Pain Points (Don't Build)
1. **Cross-platform** → Unless you personally use multiple OS
2. **Performance SLAs** → Unless someone complains
3. **Observability** → `print()` is observability for 1 user
4. **A/B testing** → You're not running experiments on yourself

---

## The Code You'll Actually Write

### Total Lines of New Code
- Scout determinism: 50 lines
- Validation wrapper: 20 lines
- State management: 30 lines
- Error handling: 40 lines
- Integration glue: 60 lines
- **Total: ~200 lines**

### Time Investment
- Writing code: 20 hours
- Testing: 10 hours
- Integration: 10 hours
- **Total: 40 hours (1 week)**

---

## How This Becomes Production Later

### Phase 1: MVP (Week 1) ← YOU ARE HERE
- Just works
- 200 lines of code
- 1 user (you)

### Phase 2: Refined (Month 1)
- Add caching where slow
- Better error messages
- 500 lines of code
- 5 users (your team)

### Phase 3: Scalable (Month 6)
- Add metrics where needed
- Multiple backends
- 2000 lines of code
- 50 users

### Phase 4: Production (Year 1)
- All the fancy stuff
- 10,000 lines of code
- 500+ users

---

## The Decision Framework

Before adding ANYTHING ask:

1. **Does it work without this?** Yes → Don't add it
2. **Will I use this next week?** No → Don't add it
3. **Is there a 10-line solution?** Yes → Use that
4. **Am I solving real or imaginary problems?** Imaginary → Stop

---

## Start Commands

```bash
# Day 1: Make scout deterministic
cp existing_scout.py mvp_scout.py
# Add: return sorted(files)
python test_scout.py

# Day 2: Wrap validation
echo "from validators import validate" > mvp_validate.py
python test_validation.py

# Day 3: Simple state
echo "import json" > mvp_state.py
python test_state.py

# Day 4: Basic errors
echo "import time" > mvp_errors.py
python test_errors.py

# Day 5: Wire it together
python run_pipeline.py "Find auth code"
```

---

## Final Reality Check

**What you're building**: A bicycle
**What you're NOT building**: A spaceship
**Why**: You need to get to the store TODAY, not Mars next decade

Every hour spent on "might need" is an hour not spent on "definitely need."

Ship the MVP. Use it. Feel the pain. Fix the actual pain. Repeat.

The best code is no code.
The second best code is deleted code.
The third best code is simple code.

Everything else is technical debt.

**Ready to build the bicycle?** Let's start with scout determinism. 4 hours. Go.