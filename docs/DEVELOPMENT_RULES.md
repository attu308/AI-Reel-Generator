# Development Rules

## Core Principles

1. Prefer AI decisions over hardcoded decisions.
2. Renderer should obey AI decisions.
3. Do not add yoga-specific logic.
4. Do not add testimonial-specific logic.
5. Avoid paid APIs unless explicitly approved.
6. Keep the system content-agnostic.
7. Favor reusable systems over one-off features.
8. When adding a renderer feature, first ask:
   "Can this be controlled by the Creative Director?"

## Architecture Principles

AI
↓
Reel Plan JSON
↓
Renderer

Never bypass the reel plan.

## Code Quality

- Prefer full function replacements.
- Explain every new file.
- Keep modules focused.
- Avoid giant utility files.

## Current Priority

Increase intelligence before increasing effects.

Good:
- Better AI decisions
- Better pacing
- Better content understanding

Bad:
- Random animations
- Cosmetic features with no AI control

## Long-Term Goal

Build an AI Creative Director, not a collection of video effects.