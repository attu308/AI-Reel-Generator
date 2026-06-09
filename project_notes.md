# MindBodyBeyondAI - Project Notes

## Technical Debt / Future Improvements

### Module 2 - Planner

* [ ] Migrate from deprecated `google.generativeai` to `google.genai`
* [ ] Add `source_file` to editing_plan.json after Gemini response
* [ ] Add `language` field to editing_plan.json
* [ ] Add planner version field
* [ ] Add Gemini response validation
* [ ] Add retry logic for Gemini failures
* [ ] Add graceful handling of malformed JSON

### Module 3 - Editor

* [ ] Replace filename matching with source_file lookup
* [ ] Skip already rendered reels
* [ ] Add render logs
* [ ] Add reel metadata JSON
* [ ] Subtitle system will use transcript.json as source of truth.
* [ ] Editing plan only decides which video segments appear.

### Future Features

* [ ] Subtitles
* [ ] Animated highlight text
* [ ] Brand logo overlay
* [ ] Background music
* [ ] CTA ending screen
* [ ] Caption generation
* [ ] Hashtag generation
* [ ] Google Drive integration
* [ ] n8n integration
* [ ] Instagram posting automation

## Decisions Made

* Faster-Whisper used for transcription
* Gemini used for AI planning
* Editing plans must use transcript timestamps only
* Planner outputs JSON, editor consumes JSON
* Modular architecture: Transcript → Plan → Reel
