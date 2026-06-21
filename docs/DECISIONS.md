# Architectural Decisions

## Renderer Obedience Model

Decision:

AI decides creative direction.

Renderer executes decisions.

Reason:

Keeps editing intelligence separate from implementation.

---

## Local First Philosophy

Decision:

Prefer local processing whenever practical.

Reason:

Reduce recurring costs.

Increase ownership.

---

## General Purpose Content

Decision:

Avoid yoga-specific logic.

Avoid testimonial-specific logic.

Reason:

System should support any content category.

---

## Gemini Creative Director

Decision:

Gemini generates reel plans.

Reason:

Strong reasoning and structured JSON output.

---

## Documentation First

Decision:

Project knowledge must live in docs/.

Reason:

Prevent context loss between sessions and AI agents.
