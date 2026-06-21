import json
from pathlib import Path
from moviepy import (
    VideoFileClip,
    AudioFileClip,
    CompositeAudioClip,
    concatenate_audioclips,
    TextClip,
    CompositeVideoClip,
    concatenate_videoclips,
    ColorClip,
    vfx,
    ImageClip
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
    """
    Load content library.
    """

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
    """
    Load Gemini reel plan.
    """

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

def load_background_music(
    reel_plan,
    settings
):
    """
    Load music selected by Gemini.
    """

    if not settings.get(
        "music_enabled",
        False
    ):
        return None

    music_file = (
        Path(__file__).parent.parent
        / "assets"
        / "music"
        / f"{reel_plan['music_style']}.mp3"
    )

    if not music_file.exists():

        print(
            f"Music file not found: "
            f"{music_file}"
        )

        return None

    print(
        f"Using music: "
        f"{music_file.name}"
    )

    return AudioFileClip(
        str(music_file)
    )

def get_visual_style(
    reel_plan
):
    return reel_plan.get(
        "visual_style",
        {}
    )

def get_audio_style(
    reel_plan
):
    return reel_plan.get(
        "audio_style",
        {}
    )

def apply_background_music(
    reel,
    reel_plan,
    settings
):
    """
    Mix background music with
    reel audio.
    """

    music = (
        load_background_music(
            reel_plan,
            settings
        )
    )

    if music is None:
        return reel

    intensity = (
        reel_plan
        .get(
            "audio_style",
            {}
        )
        .get(
            "music_intensity",
            "medium"
        )
    )

    volume_map = {
        "low": 0.08,
        "medium": 0.15,
        "high": 0.25
    }

    music_volume = (
        volume_map.get(
            intensity,
            0.15
        )
    )

    print(
        f"Music intensity: "
        f"{intensity}"
    )

    music = (
        music
        .with_volume_scaled(
            music_volume
        )
    )

    while (
        music.duration
        <
        reel.duration
    ):

        music = concatenate_audioclips(
            [music, music]
        )

    music = music.subclipped(
        0,
        reel.duration
    )

    if reel.audio:

        final_audio = (
            CompositeAudioClip(
                [
                    reel.audio,
                    music
                ]
            )
        )

    else:

        final_audio = music

    return reel.with_audio(
        final_audio
    )

def get_intro_image_path(
    reel_plan
):
    """
    Get intro image selected
    by Gemini.
    """

    return (
        Path(__file__).parent.parent
        / "assets"
        / "intro"
        / reel_plan[
            "intro_image"
        ]
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

    visual_energy = (
        reel_plan
        .get(
            "visual_style",
            {}
        )
        .get(
            "visual_energy",
            5
        )
    )

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

        original_duration = (
            segment["end"]
            -
            segment["start"]
        )

        if visual_energy <= 3:

            keep_ratio = 1.0

        elif visual_energy <= 6:

            keep_ratio = 0.9

        else:

            keep_ratio = 0.75

        target_duration = (
            original_duration
            *
            keep_ratio
        )

        safe_end = min(
            segment["start"]
            +
            target_duration,
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

        clip = format_for_reel(
            clip
        )

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
                safe_end
            )
        )

        clip = (
            add_subtitles_to_clip(
                clip,
                subtitle_segments,
                segment[
                    "start"
                ],
                reel_plan
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
    Professional branded intro.
    """

    duration = 2.5

    background_path = (
        get_intro_image_path(
            reel_plan
        )
    )

    background = (
        ImageClip(
            str(background_path)
        )
        .resized(
            height=1920
        )
        .with_duration(
            duration
        )
    )

    background = CompositeVideoClip(
        [
            background.with_opacity(
                0.45
            ),
            ColorClip(
                size=(1080, 1920),
                color=(0, 0, 0)
            )
            .with_duration(
                duration
            )
            .with_opacity(
                0.55
            )
        ],
        size=(1080, 1920)
    )

    brand = TextClip(
        text="MINDBODYBEYOND",
        font_size=42,
        color="#D0D0D0"
    )

    brand = (
        brand
        .with_duration(
            duration
        )
        .with_position(
            ("center", 220)
        )
    )

    hook = TextClip(
        text=reel_plan[
            "hook_title"
        ],
        font_size=115,
        color="white",
        stroke_color="black",
        stroke_width=4,
        size=(900, 700),
        method="caption",
        text_align="center"
    )

    hook = (
        hook
        .with_duration(
            duration
        )
        .with_position(
            "center"
        )
    )

    title = TextClip(
        text=reel_plan[
            "reel_title"
        ],
        font_size=50,
        color="#FFD700",
        size=(900, 200),
        method="caption",
        text_align="center"
    )

    title = (
        title
        .with_duration(
            duration
        )
        .with_position(
            ("center", 1340)
        )
    )

    divider = (
        ColorClip(
            size=(500, 5),
            color=(255, 215, 0)
        )
        .with_duration(
            duration
        )
        .with_position(
            ("center", 1280)
        )
    )

    intro = CompositeVideoClip(
        [
            background,
            brand,
            hook,
            divider,
            title
        ],
        size=(1080, 1920)
    )

    hook_animation = (
        reel_plan
        .get(
            "visual_style",
            {}
        )
        .get(
            "hook_animation",
            "fade"
        )
    )

    if (
        hook_animation
        ==
        "zoom"
    ):

        intro = (
            intro
            .resized(
                lambda t:
                1 + (
                    0.08
                    *
                    (
                        t
                        /
                        duration
                    )
                )
            )
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

    visual_energy = (
        reel_plan
        .get(
            "visual_style",
            {}
        )
        .get(
            "visual_energy",
            5
        )
    )

    transition_style = (
        reel_plan
        .get(
            "visual_style",
            {}
        )
        .get(
            "transition_style",
            "crossfade"
        )
    )

    if visual_energy <= 3:

        transition_duration = 0.60

    elif visual_energy <= 6:

        transition_duration = 0.35

    else:

        transition_duration = 0.15

    print(
        f"Visual Energy: "
        f"{visual_energy}"
    )

    print(
        f"Transition Duration: "
        f"{transition_duration}"
    )

    processed_clips = []

    for i, clip in enumerate(
        all_clips
    ):

        if i > 0:

            if (
                transition_style
                ==
                "crossfade"
            ):

                clip = (
                    clip
                    .with_start(
                        processed_clips[-1].end
                        -
                        transition_duration
                    )
                    .with_effects(
                        [
                            vfx.CrossFadeIn(
                                transition_duration
                            )
                        ]
                    )
                )

            else:

                clip = (
                    clip
                    .with_start(
                        processed_clips[-1].end
                    )
                )

        processed_clips.append(
            clip
        )

    reel = CompositeVideoClip(
        processed_clips,
        size=(1080, 1920)
    )

    settings = (
        load_settings()
    )

    reel = (
        apply_background_music(
            reel,
            reel_plan,
            settings
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

def split_words_into_chunks(
    words,
    words_per_chunk=4
):
    """
    Split word timestamp data
    into chunks.
    """

    chunks = []

    for i in range(
        0,
        len(words),
        words_per_chunk
    ):

        chunk_words = (
            words[
                i:i + words_per_chunk
            ]
        )

        chunks.append(
            chunk_words
        )

    return chunks

def create_highlighted_subtitle_clip(
    full_text,
    highlighted_word,
    duration,
    video_width,
    video_height,
    caption_position="lower_third"
):
    """
    Subtitle with one word
    highlighted.
    """

    is_vertical = (
        video_height >
        video_width
    )

    if is_vertical:

        subtitle_width = int(
            video_width * 0.8
        )

        font_size = 50

    else:

        subtitle_width = int(
            video_width * 0.7
        )

        font_size = 60

    if caption_position == "center":

        subtitle_y = int(
            video_height * 0.55
        )

    else:

        subtitle_y = int(
            video_height * 0.82
        )

    highlighted_text = (
        full_text.replace(
            highlighted_word,
            f"[{highlighted_word}]",
            1
        )
    )

    subtitle = TextClip(
        text=highlighted_text,
        font_size=font_size,
        color="white",
        stroke_color="black",
        stroke_width=3,
        size=(
            subtitle_width,
            250
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
    clip_start_time,
    reel_plan
):
    """
    Add word-level subtitles.
    Visual energy controls pacing.
    """

    overlays = [clip]

    visual_energy = (
        reel_plan
        .get(
            "visual_style",
            {}
        )
        .get(
            "visual_energy",
            5
        )
    )

    if visual_energy <= 3:

        words_per_chunk = 5

    elif visual_energy <= 6:

        words_per_chunk = 4

    else:

        words_per_chunk = 2

    print(
        f"Visual Energy: "
        f"{visual_energy}"
    )

    print(
        f"Words Per Chunk: "
        f"{words_per_chunk}"
    )

    for segment in subtitle_segments:

        if not segment.get(
            "words"
        ):
            continue

        chunks = (
            split_words_into_chunks(
                segment["words"],
                words_per_chunk
            )
        )

        for chunk in chunks:

            chunk_text = " ".join(
                [
                    word["word"]
                    for word in chunk
                ]
            )

            chunk_start = (
                chunk[0]["start"]
            )

            chunk_end = (
                chunk[-1]["end"]
            )

            chunk_duration = (
                chunk_end
                -
                chunk_start
            )

            for word in chunk:

                word_start = (
                    word["start"]
                )

                word_duration = (
                    max(
                        0.08,
                        word["end"]
                        -
                        word["start"]
                    )
                )

                subtitle = (
                    create_highlighted_subtitle_clip(
                        chunk_text,
                        word["word"],
                        word_duration,
                        clip.w,
                        clip.h,
                        reel_plan
                        .get(
                            "visual_style",
                            {}
                        )
                        .get(
                            "caption_position",
                            "lower_third"
                        )
                    )
                )

                subtitle = (
                    subtitle
                    .with_start(
                        (
                            word_start
                            -
                            clip_start_time
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