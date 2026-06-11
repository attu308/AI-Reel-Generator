import json
from pathlib import Path
from moviepy import (
    VideoFileClip,
    TextClip,
    CompositeVideoClip,
    concatenate_videoclips,
    ColorClip
)

def load_settings():

    settings_file = (
        Path(__file__).parent.parent
        / "config"
        / "settings.json"
    )

    with open(
        settings_file,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(
            file
        )

def load_content_library():

    library_file = (
        Path(__file__).parent.parent
        / "data"
        / "content_library.json"
    )

    with open(
        library_file,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(
            file
        )


def load_reel_plan():

    plan_file = (
        Path(__file__).parent.parent
        / "data"
        / "reel_plan.json"
    )

    with open(
        plan_file,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(
            file
        )


def get_selected_segments(
    content_library,
    reel_plan
):
    """
    Resolve segment IDs into
    actual segment objects
    while preserving the
    order chosen by Gemini.
    """

    selected_segments = []

    segments_by_id = {}

    for segment in content_library[
        "segments"
    ]:

        segments_by_id[
            segment["id"]
        ] = segment

    for segment_id in reel_plan[
        "segment_ids"
    ]:

        if segment_id in (
            segments_by_id
        ):

            selected_segments.append(
                segments_by_id[
                    segment_id
                ]
            )

        else:

            print(
                f"Missing ID: "
                f"{segment_id}"
            )

    return selected_segments

def save_selected_segments(
    selected_segments
):

    output_file = (
        Path(__file__).parent.parent
        / "data"
        / "selected_segments.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            selected_segments,
            file,
            indent=4,
            ensure_ascii=False
        )

    return output_file

def print_selected_segments(
    selected_segments
):
    """
    Print selected segments.
    """

    for segment in (
        selected_segments
    ):

        print(
            "\n----------------"
        )

        print(
            f"ID: "
            f"{segment['id']}"
        )

        print(
            f"VIDEO: "
            f"{segment['source_video']}"
        )

        print(
            f"START: "
            f"{segment['start']}"
        )

        print(
            f"END: "
            f"{segment['end']}"
        )

        print(
            f"TEXT: "
            f"{segment['text']}"
        )

def add_highlights_to_clip(
    clip,
    highlights
):
    """
    Add highlight overlays.
    """

    overlays = [clip]

    for highlight in highlights:

        highlight_clip = (
            create_highlight_clip(
                highlight["text"],
                min(
                    2.5,
                    clip.duration
                )
            )
        )

        overlays.append(
            highlight_clip
        )

    return CompositeVideoClip(
        overlays
    )

def format_for_reel(
    clip
):
    """
    Convert any clip into
    1080x1920 reel format.
    """

    REEL_WIDTH = 1080
    REEL_HEIGHT = 1920

    is_vertical = (
        clip.h >
        clip.w
    )

    if is_vertical:

        clip = clip.resized(
            height=REEL_HEIGHT
        )

        if clip.w > REEL_WIDTH:

            x1 = (
                clip.w
                -
                REEL_WIDTH
            ) / 2

            clip = clip.cropped(
                x1=x1,
                x2=x1 + REEL_WIDTH
            )

        elif clip.w < REEL_WIDTH:

            background = ColorClip(
                size=(
                    REEL_WIDTH,
                    REEL_HEIGHT
                ),
                color=(
                    0,
                    0,
                    0
                )
            ).with_duration(
                clip.duration
            )

            clip = CompositeVideoClip(
                [
                    background,
                    clip.with_position(
                        "center"
                    )
                ],
                size=(
                    REEL_WIDTH,
                    REEL_HEIGHT
                )
            )

    else:

        background = (
            clip
            .resized(
                height=REEL_HEIGHT
            )
            .with_opacity(
                0.25
            )
        )

        foreground = (
            clip
            .resized(
                width=REEL_WIDTH
            )
            .with_position(
                "center"
            )
        )

        clip = CompositeVideoClip(
            [
                background,
                foreground
            ],
            size=(
                REEL_WIDTH,
                REEL_HEIGHT
            )
        )

    print(
        f"Reel clip size: "
        f"{clip.w} x {clip.h}"
    )

    return clip

def create_clips(
    selected_segments,
    reel_plan,
    settings
):
    """
    Create MoviePy clips from
    selected segments.
    """

    clips = []

    input_folder = (
        Path(__file__).parent.parent
        /
        settings[
            "input_folder"
        ].replace(
            "../",
            ""
        )
    )

    for segment in (
        selected_segments
    ):

        video_path = (
            input_folder
            /
            segment[
                "source_video"
            ]
        )

        print(
            f"Loading: "
            f"{video_path.name}"
        )

        video = VideoFileClip(
            str(
                video_path
            )
        )

        if (
            segment["end"]
            >
            video.duration
        ):

            print(
                f"Clamping segment "
                f"{segment['id']} "
                f"from "
                f"{segment['end']} "
                f"to "
                f"{video.duration}"
            )

        safe_end = min(
            segment["end"],
            video.duration - 0.05
        )

        clip = (
            video
            .subclipped(
                segment[
                    "start"
                ],
                safe_end
            )
        )

        clip = format_for_reel(clip)

        transcript_data = (
            load_transcript(
                segment[
                    "source_video"
                ],
                settings
            )
        )

        subtitle_segments = (
            get_subtitle_segments(
                transcript_data,
                segment[
                    "start"
                ],
                segment[
                    "end"
                ]
            )
        )

        clip = (
            add_subtitles_to_clip(
                clip,
                subtitle_segments,
                segment[
                    "start"
                ]
            )
        )

        highlights = (
            get_highlights_for_segment(
                reel_plan,
                segment[
                    "id"
                ]
            )
        )

        clip = (
            add_highlights_to_clip(
                clip,
                highlights
            )
        )

        if len(clips) == 0:

            clip = (
                add_hook_to_first_clip(
                    clip,
                    reel_plan
                )
            )

        clips.append(
            clip
        )
    
    return clips

def create_intro_card(
    reel_plan
):
    """
    Professional intro card.
    """

    background = (
        ColorClip(
            size=(1080, 1920),
            color=(15, 15, 15)
        )
        .with_duration(2)
    )

    brand = TextClip(
        text="MINDBODYBEYOND",
        font_size=45,
        color="white"
    )

    brand = (
        brand
        .with_duration(2)
        .with_position(
            ("center", 250)
        )
    )

    hook = TextClip(
        text=reel_plan[
            "hook_title"
        ],
        font_size=80,
        color="white",
        stroke_color="black",
        stroke_width=3,
        size=(900, 600),
        method="caption",
        text_align="center"
    )

    hook = (
        hook
        .with_duration(2)
        .with_position(
            "center"
        )
    )

    title = TextClip(
        text=reel_plan[
            "reel_title"
        ],
        font_size=45,
        color="yellow",
        size=(900, 150),
        method="caption",
        text_align="center"
    )

    title = (
        title
        .with_duration(2)
        .with_position(
            ("center", 1400)
        )
    )

    intro = CompositeVideoClip(
        [
            background,
            brand,
            hook,
            title
        ],
        size=(1080, 1920)
    )

    return intro

def build_reel(
    clips,
    reel_plan
):
    """
    Combine clips into reel.
    """

    intro = (
        create_intro_card(
            reel_plan
        )
    )

    all_clips = [
        intro
    ]

    all_clips.extend(
        clips
    )

    reel = (
        concatenate_videoclips(
            all_clips,
            method="compose"
        )
    )

    return reel

def export_reel(
    reel
):
    """
    Export reel.
    """

    output_file = (
        Path(__file__).parent.parent
        / "output"
        / "multi_video_reel.mp4"
    )

    reel.write_videofile(
        str(output_file),
        codec="libx264",
        audio_codec="aac"
    )

    return output_file

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
            ("center", 300)
        )
    )

    return highlight

def get_highlights_for_segment(
    reel_plan,
    segment_id
):
    """
    Get highlights assigned to
    a segment.
    """

    highlights = []

    for highlight in reel_plan[
        "highlight_phrases"
    ]:

        if (
            highlight[
                "segment_id"
            ]
            ==
            segment_id
        ):

            highlights.append(
                highlight
            )

    return highlights

def add_hook_to_first_clip(
    clip,
    reel_plan
):
    """
    Add hook title to the
    first clip.
    """

    hook_text = (
        reel_plan[
            "hook_title"
        ]
    )

    hook_clip = (
        create_hook_clip(
            hook_text,
            min(
                3,
                clip.duration
            )
        )
    )

    return CompositeVideoClip(
        [
            clip,
            hook_clip
        ]
    )

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

def create_subtitle_clip(
    text,
    duration,
    video_width,
    video_height
):

    is_vertical = (
        video_height
        >
        video_width
    )

    if is_vertical:

        subtitle_y = int(
            video_height * 0.82
        )

        subtitle_width = int(
            video_width * 0.8
        )

        font_size = 40

    else:

        subtitle_y = int(
            video_height * 0.85
        )

        subtitle_width = int(
            video_width * 0.7
        )

        font_size = 55

    subtitle = TextClip(
        text=text,
        font_size=font_size,
        color="white",
        stroke_color="black",
        stroke_width=3,
        size=(
            subtitle_width,
            200
        ),
        method="caption",
        text_align="center"
    )

    subtitle = (
        subtitle
        .with_duration(duration)
        .with_position(
            (
                "center",
                subtitle_y
            )
        )
    )

    return subtitle

def load_transcript(
    source_video,
    settings
):
    """
    Load transcript belonging
    to a source video.
    """

    transcripts_folder = (
        Path(__file__).parent.parent
        /
        settings[
            "transcripts_folder"
        ].replace(
            "../",
            ""
        )
    )

    transcript_file = (
        transcripts_folder
        /
        f"{Path(source_video).stem}_transcript.json"
    )

    with open(
        transcript_file,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(
            file
        )
    
def get_subtitle_segments(
    transcript_data,
    start_time,
    end_time
):
    """
    Find transcript segments
    overlapping current clip.
    """

    subtitle_segments = []

    for segment in transcript_data[
        "segments"
    ]:

        if (
            segment["start"]
            < end_time
            and
            segment["end"]
            > start_time
        ):

            subtitle_segments.append(
                segment
            )

    return subtitle_segments

def add_subtitles_to_clip(
    clip,
    subtitle_segments,
    clip_start_time
):
    """
    Add chunked subtitles.
    """

    overlays = [clip]

    for segment in (
        subtitle_segments
    ):

        chunks = (
            split_text_into_chunks(
                segment["text"],
                words_per_chunk=4
            )
        )

        if not chunks:
            continue

        segment_duration = (
            segment["end"]
            -
            segment["start"]
        )

        chunk_duration = (
            segment_duration
            /
            len(chunks)
        )

        for i, chunk in enumerate(
            chunks
        ):

            subtitle = (
                create_subtitle_clip(
                    chunk,
                    chunk_duration,
                    clip.w,
                    clip.h
                )
            )

            subtitle = (
                subtitle.with_start(
                    (
                        segment["start"]
                        -
                        clip_start_time
                    )
                    +
                    (
                        i
                        *
                        chunk_duration
                    )
                )
            )

            overlays.append(
                subtitle
            )

    return CompositeVideoClip(
        overlays
    )

if __name__ == "__main__":

    settings = (
        load_settings()
    )

    content_library = (
        load_content_library()
    )

    reel_plan = (
        load_reel_plan()
    )

    selected_segments = (
        get_selected_segments(
            content_library,
            reel_plan
        )
    )

    clips = (
        create_clips(
            selected_segments,
            reel_plan,
            settings
        )
    )

    reel = (
        build_reel(
            clips, reel_plan
        )
    )

    output_file = (
        export_reel(
            reel
        )
    )

    print(
        f"\nSaved: "
        f"{output_file}"
    )