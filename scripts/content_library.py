import json
from pathlib import Path


def load_settings():
    """
    Load project configuration.
    """

    config_path = (
        Path(__file__).parent.parent
        / "config"
        / "settings.json"
    )

    with open(
        config_path,
        "r",
        encoding="utf-8"
    ) as file:
        settings = json.load(file)

    return settings


def get_transcript_files(
    settings
):
    """
    Find all transcript files.
    """

    transcripts_folder = (
        Path(__file__).parent.parent
        /
        settings[
            "transcripts_folder"
        ].replace("../", "")
    )

    transcript_files = list(
        transcripts_folder.glob(
            "*_transcript.json"
        )
    )

    return transcript_files

def load_transcript(
    transcript_file
):
    """
    Load a transcript JSON file.
    """

    with open(
        transcript_file,
        "r",
        encoding="utf-8"
    ) as file:

        transcript_data = json.load(
            file
        )

    return transcript_data


def count_segments(
    transcript_data
):
    """
    Count transcript segments.
    """

    return len(
        transcript_data["segments"]
    )

def build_content_library():
    """
    Create empty content library.
    """

    return {
        "segments": []
    }

def save_content_library(
    content_library
):
    """
    Save content library.
    """

    data_folder = (
        Path(__file__).parent.parent
        / "data"
    )

    data_folder.mkdir(
        exist_ok=True
    )

    output_file = (
        data_folder
        / "content_library.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            content_library,
            file,
            indent=4,
            ensure_ascii=False
        )

    return 

def build_content_library(
    transcript_files
):
    """
    Build content library from all transcripts.
    """

    content_library = {
        "segments": []
    }

    for transcript_file in transcript_files:

        transcript_data = load_transcript(
            transcript_file
        )

        source_video = (
            transcript_data[
                "source_file"
            ]
        )

        for segment in transcript_data[
            "segments"
        ]:

            content_library[
                "segments"
            ].append(
                {
                    "id": len(
                        content_library[
                            "segments"
                        ]
                    ),

                    "source_video":
                    source_video,

                    "start":
                    segment["start"],

                    "end":
                    segment["end"],

                    "duration":
                    round(
                        segment["end"]
                        -
                        segment["start"],
                        2
                    ),

                    "text":
                    segment["text"]
                }
            )

    return content_library

def save_content_library(
    content_library
):
    """
    Save content library.
    """

    data_folder = (
        Path(__file__).parent.parent
        / "data"
    )

    data_folder.mkdir(
        exist_ok=True
    )

    output_file = (
        data_folder
        / "content_library.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            content_library,
            file,
            indent=4,
            ensure_ascii=False
        )

    return output_file

def print_library_stats(
    content_library
):
    """
    Print content library statistics.
    """

    videos = set()

    total_duration = 0

    for segment in content_library[
        "segments"
    ]:

        videos.add(
            segment[
                "source_video"
            ]
        )

        total_duration += (
            segment[
                "duration"
            ]
        )

    print(
        f"Videos: {len(videos)}"
    )

    print(
        f"Segments: "
        f"{len(content_library['segments'])}"
    )

    print(
        f"Content Duration: "
        f"{round(total_duration, 1)}s"
    )

def search_segments(
    content_library,
    query
):
    """
    Search content library for segments
    containing a keyword.
    """

    matches = []

    query = query.lower()

    for segment in content_library[
        "segments"
    ]:

        if query in segment[
            "text"
        ].lower():

            matches.append(
                segment
            )

    return matches

def get_top_segments(
    content_library,
    min_duration=4
):
    """
    Get useful segments for reel creation.
    """

    segments = []

    for segment in content_library[
        "segments"
    ]:

        if (
            segment[
                "duration"
            ] >= min_duration
        ):

            segments.append(
                segment
            )

    segments = sorted(
        segments,
        key=lambda x: x[
            "duration"
        ],
        reverse=True
    )

    return segments

def create_library_summary(
    content_library
):
    """
    Convert content library into
    text for Gemini.
    """

    lines = []

    for segment in content_library[
        "segments"
    ]:

        lines.append(
            f"ID: {segment['id']}\n"
            f"VIDEO: {segment['source_video']}\n"
            f"START: {segment['start']}\n"
            f"END: {segment['end']}\n"
            f"TEXT: {segment['text']}\n"
        )

    return "\n".join(
        lines
    )

def save_library_summary(
    summary_text
):
    """
    Save library summary.
    """

    data_folder = (
        Path(__file__).parent.parent
        / "data"
    )

    output_file = (
        data_folder
        / "library_summary.txt"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            summary_text
        )

    return output_file

if __name__ == "__main__":

    settings = load_settings()

    transcript_files = (
        get_transcript_files(
            settings
        )
    )

    print(
        f"Found {len(transcript_files)} transcripts"
    )

    content_library = (
        build_content_library(
            transcript_files
        )
    )

    print_library_stats(
        content_library
    )

    output_file = (
        save_content_library(
            content_library
        )
    )

    print(
        f"Saved: {output_file}"
    )

    summary_text = (
        create_library_summary(
            content_library
        )
    )

    summary_file = (
        save_library_summary(
            summary_text
        )
    )

    print(
        f"Saved: {summary_file}"
    )