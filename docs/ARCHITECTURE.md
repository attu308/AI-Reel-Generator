# Architecture

## High-Level Pipeline

Input Videos
↓
Transcription
↓
Content Library Generation
↓
Creative Director (Gemini)
↓
Reel Plan JSON
↓
Renderer
↓
Final Reel

---

## Technologies

### Core

* Python
* MoviePy
* Faster-Whisper
* FFmpeg

### AI

* Google Gemini

---

## Current Folder Structure

```text
MindBodyBeyondAI/

assets/
    intro/
    music/

config/
    settings.json

data/
    content_library.json
    reel_plan.json

input/
    source videos

output/
    generated reels

plans/
    legacy planning outputs

scripts/
    transcribe.py
    planner.py
    reel_builder.py

transcripts/
    transcript JSON files
```

## Major Components

### transcribe.py

Responsibilities:

* Load videos
* Run Faster Whisper
* Generate transcripts
* Generate word timestamps

Outputs:

```text
transcripts/*.json
```

### planner.py

Responsibilities:

* Load content library
* Call Gemini
* Generate creative direction
* Generate reel plan

Outputs:

```text
data/reel_plan.json
```

### reel_builder.py

Responsibilities:

* Load reel plan
* Load source clips
* Build reel
* Apply captions
* Apply highlights
* Apply intro card
* Apply music
* Export final reel

Outputs:

```text
output/multi_video_reel.mp4
```

## Current AI Decisions

Gemini currently controls:

* reel_title
* hook
* hook_title
* segment_ids
* highlight_phrases
* theme
* music_style
* intro_image
* caption_style
* caption_position
* transition_style
* hook_animation
* visual_energy
* music_intensity

## Current Renderer Obedience

Renderer currently obeys:

* music_style
* music_intensity
* intro_image
* caption_position
* transition_style
* hook_animation
* visual_energy (partial)

## Architectural Direction

Move toward:

AI decides
↓
JSON reel plan
↓
Renderer obeys

Avoid hardcoded creative decisions inside renderer.
