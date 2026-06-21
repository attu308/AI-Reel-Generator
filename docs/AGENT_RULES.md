# Agent Rules

## Required Startup Procedure

Before making any code changes:

Read:

* PROJECT_VISION.md
* ARCHITECTURE.md
* CURRENT_STATE.md
* ROADMAP.md
* TASKS.md
* DEVELOPMENT_RULES.md

Summarize understanding before implementation.

---

## Architecture Rules

Creative decisions belong in AI.

Execution belongs in the renderer.

Prefer:

AI
↓
reel_plan.json
↓
renderer

Avoid hardcoded creative logic.

---

## Safety Rules

Do not delete files without approval.

Do not remove working features.

Do not rewrite architecture without approval.

Do not introduce paid services unless requested.

---

## Documentation Rules

Whenever architecture changes:

Update:

* CURRENT_STATE.md
* ARCHITECTURE.md
* TASKS.md

---

## Testing Rules

Every feature must include:

* verification method
* expected result
* rollback path

---

## Scope Rules

Do only the requested task.

Do not perform unrelated refactors.

Do not introduce speculative features.

---

## Long Term Goal

Build an AI Creative Director.

Do not optimize for temporary visual effects.

Optimize for intelligent editing decisions.
 