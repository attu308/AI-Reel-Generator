import json
from pathlib import Path
from moviepy import (
    VideoFileClip,
    TextClip,
    CompositeVideoClip,
    concatenate_videoclips
)
from moviepy import vfx

def load_settings():
    """
    Load project configuration from settings.json.
    """

    config_path = Path(__file__).parent.parent / "config" / "settings.json"

    with open(config_path, "r", encoding="utf-8") as file:
        settings = json.load(file)

    return settings

def get_editing_plan_files(settings):
    """
    Find all editing plan JSON files.
    """

    plans_folder = (
        Path(__file__).parent.parent /
        settings["plans_folder"].replace("../", "")
    )

    editing_plan_files = list(
        plans_folder.glob("*_editing_plan.json")
    )

    return editing_plan_files

def find_source_video(editing_plan_file, settings):
    """
    Find the source video that belongs
    to an editing plan.
    """

    video_stem = (
        editing_plan_file.stem
        .replace("_editing_plan", "")
    )

    input_folder = (
        Path(__file__).parent.parent /
        settings["input_folder"].replace("../", "")
    )

    for file in input_folder.iterdir():
        if file.stem == video_stem:
            return file

    return None

def find_transcript_file(
    editing_plan_file,
    settings
):
    """
    Find transcript file that belongs
    to an editing plan.
    """

    video_stem = (
        editing_plan_file.stem
        .replace("_editing_plan", "")
    )

    transcripts_folder = (
        Path(__file__).parent.parent /
        settings["transcripts_folder"].replace("../", "")
    )

    transcript_file = (
        transcripts_folder /
        f"{video_stem}_transcript.json"
    )

    return transcript_file

def load_editing_plan(editing_plan_file):
    """
    Load an editing plan JSON file.
    """

    with open(
        editing_plan_file,
        "r",
        encoding="utf-8"
    ) as file:
        editing_plan = json.load(file)

    return editing_plan

def load_transcript(transcript_file):
    """
    Load a transcript JSON file.
    """

    with open(
        transcript_file,
        "r",
        encoding="utf-8"
    ) as file:
        transcript_data = json.load(file)

    return transcript_data

def load_video(video_path):
    """
    Load a video using MoviePy.
    """

    video = VideoFileClip(
        str(video_path)
    )

    return video

def split_text_into_chunks(
    text,
    words_per_chunk=4
):
    """
    Split subtitle text into
    smaller chunks.
    """

    words = text.split()

    chunks = []

    for i in range(
        0,
        len(words),
        words_per_chunk
    ):
        chunk = " ".join(
            words[
                i:i + words_per_chunk
            ]
        )

        chunks.append(chunk)

    return chunks

def get_subtitle_segments(
    transcript_data,
    start_time,
    end_time
):
    """
    Find transcript segments that overlap
    a reel segment.
    """

    subtitle_segments = []

    for segment in transcript_data["segments"]:

        if (
            segment["start"] < end_time
            and
            segment["end"] > start_time
        ):
            subtitle_segments.append(
                segment
            )

    return subtitle_segments

def create_subtitle_clip(
    text,
    duration
):

    subtitle = TextClip(
        text=text,
        font_size=40,
        color="white",
        stroke_color="black",
        stroke_width=3,
        size=(450, 200),
        method="caption",
        text_align="center"
    )

    subtitle = (
        subtitle
        .with_duration(duration)
        .with_position(
            ("center", 700)
        )
    )

    return subtitle

def create_highlight_clip(
    text,
    duration
):
    """
    Create highlight text overlay.
    """

    highlight = TextClip(
        text=text.upper(),
        font_size=60,
        color="yellow",
        stroke_color="black",
        stroke_width=4,
        size=(400, 150),
        method="caption",
        text_align="center"
    )

    highlight = (
        highlight
        .with_duration(duration)
        .with_position(
            ("center", 180)
        )
    )

    return highlight

def create_hook_clip(
    text,
    duration
):
    """
    Create opening hook overlay.
    """

    hook = TextClip(
        text=text,
        font_size=55,
        color="white",
        stroke_color="black",
        stroke_width=5,
        size=(470, 120),
        method="caption",
        text_align="center"
    )

    hook = (
        hook
        .with_duration(duration)
        .with_position(
            ("center", 180)
        )
    )

    return hook

def get_highlights_for_segment(
    editing_plan,
    start_time,
    end_time
):
    """
    Find highlight phrases that overlap
    the current clip.
    """

    highlights = []

    for highlight in editing_plan[
        "highlight_phrases"
    ]:

        if (
            highlight["start"] < end_time
            and
            highlight["end"] > start_time
        ):
            highlights.append(
                highlight
            )

    return highlights

def add_subtitles_to_clip(
    clip,
    subtitle_segments,
    clip_start_time
):
    """
    Add subtitles to a clip.
    """

    overlays = [clip]

    for segment in subtitle_segments:

        chunks = split_text_into_chunks(
            segment["text"],
            words_per_chunk=4
        )

        if not chunks:
            continue

        segment_duration = (
            segment["end"] - segment["start"]
        )

        chunk_duration = (
            segment_duration / len(chunks)
        )

        for i, chunk in enumerate(chunks):

            subtitle = create_subtitle_clip(
                chunk,
                chunk_duration
            )

            subtitle = subtitle.with_start(
                (
                    segment["start"]
                    - clip_start_time
                )
                +
                (
                    i * chunk_duration
                )
            )

            overlays.append(
                subtitle
            )

    return CompositeVideoClip(
        overlays
    )

def extract_clip(
    video,
    start_time,
    end_time
):
    """
    Extract a clip from the video.
    """

    clip = video.subclipped(
        start_time,
        end_time
    )

    return clip

def build_clips(
    video,
    editing_plan,
    transcript_data
):
    """
    Extract all recommended segments.
    """

    clips = []

    for segment in editing_plan[
        "recommended_segments"
    ]:

        clip = extract_clip(
            video,
            segment["start"],
            segment["end"]
        )

        subtitle_segments = (
            get_subtitle_segments(
                transcript_data,
                segment["start"],
                segment["end"]
            )
        )

        clip = add_subtitles_to_clip(
            clip,
            subtitle_segments,
            segment["start"]
        )

        highlights = (
            get_highlights_for_segment(
                editing_plan,
                segment["start"],
                segment["end"]
            )
        )

        overlays = [clip]

        for highlight in highlights:

            highlight_clip = (
                create_highlight_clip(
                    highlight["text"],
                    highlight["end"]
                    - highlight["start"]
                )
            )

            highlight_clip = (
                highlight_clip.with_start(
                    highlight["start"]
                    - segment["start"]
                )
            )

            overlays.append(
                highlight_clip
            )

        clip = CompositeVideoClip(
            overlays
        )

        clips.append(
            clip
        )

    return clips

def build_reel(
    clips,
    editing_plan
):
    """
    Combine clips with transitions.
    """

    transition_duration = 0.25

    faded_clips = []

    for i, clip in enumerate(clips):

        if i > 0:
            clip = clip.with_effects([
                vfx.CrossFadeIn(
                    transition_duration
                )
            ])

        faded_clips.append(
            clip
        )

    reel = concatenate_videoclips(
        faded_clips,
        method="compose",
        padding=-transition_duration
    )

    return reel

def save_clip(
    clip,
    output_path
):
    """
    Save a clip to disk.
    """

    clip.write_videofile(
        str(output_path),
        codec="libx264",
        audio_codec="aac"
    )

def get_output_clip_path(
    editing_plan_file,
    settings
):
    """
    Build output path for a test clip.
    """

    output_folder = (
        Path(__file__).parent.parent /
        settings["output_folder"].replace("../", "")
    )

    return (
        output_folder /
        f"{editing_plan_file.stem}_test_clip.mp4"
    )

def get_reel_output_path(
    editing_plan_file,
    settings
):
    """
    Output path for final reel.
    """

    output_folder = (
        Path(__file__).parent.parent /
        settings["output_folder"].replace("../", "")
    )

    video_name = (
        editing_plan_file.stem
        .replace("_editing_plan", "")
    )

    return (
        output_folder /
        f"{video_name}_reel.mp4"
    )

if __name__ == "__main__":

    settings = load_settings()

    editing_plan_files = (
        get_editing_plan_files(settings)
    )

    for editing_plan_file in editing_plan_files:

        print(
            f"\nProcessing: {editing_plan_file.name}"
        )

        editing_plan = load_editing_plan(
            editing_plan_file
        )

        source_video = find_source_video(
            editing_plan_file,
            settings
        )

        transcript_file = (
            find_transcript_file(
                editing_plan_file,
                settings
            )
        )

        transcript_data = (
            load_transcript(
                transcript_file
            )
        )

        video = load_video(
            source_video
        )

        clips = build_clips(
            video,
            editing_plan,
            transcript_data
        )

        reel = build_reel(
            clips ,
            editing_plan
        )

        output_path = (
            get_reel_output_path(
                editing_plan_file,
                settings
            )
        )

        print(
            f"Saving reel: {output_path}"
        )

        reel.write_videofile(
            str(output_path),
            codec="libx264",
            audio_codec="aac"
        )

        reel.close()

        for clip in clips:
            clip.close()

        video.close()

        print("Done.")