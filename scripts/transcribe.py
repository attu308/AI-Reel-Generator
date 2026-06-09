import json
from pathlib import Path

from faster_whisper import WhisperModel

def load_settings():
    """
    Load project configuration from settings.json.
    """

    config_path = Path(__file__).parent.parent / "config" / "settings.json"

    with open(config_path, "r", encoding="utf-8") as file:
        settings = json.load(file)

    return settings


def get_video_files(settings):
    """
    Find all supported video files in the input folder.
    """

    input_folder = (
        Path(__file__).parent.parent /
        settings["input_folder"].replace("../", "")
    )

    supported_extensions = [".mp4", ".mov", ".mkv", ".avi"]

    video_files = []

    for file in input_folder.iterdir():
        if file.suffix.lower() in supported_extensions:
            video_files.append(file)

    return video_files

def load_model(settings):
    """
    Load the Faster-Whisper model.
    """

    model = WhisperModel(
        settings["whisper_model"],
        device="cpu",
        compute_type="int8"
    )

    return model

def transcribe_video(model, video_path):
    """
    Transcribe a single video file.
    """

    segments, info = model.transcribe(
        str(video_path),
        beam_size=5
    )

    return segments, info

def save_transcript(video_path, segments, info, settings):
    """
    Save transcript data to a JSON file.
    """

    transcripts_folder = (
        Path(__file__).parent.parent /
        settings["transcripts_folder"].replace("../", "")
    )

    transcript_data = {
        "source_file": video_path.name,
        "language": info.language,
        "duration": info.duration,
        "segments": []
    }

    for segment in segments:
        transcript_data["segments"].append(
            {
                "start": round(segment.start, 2),
                "end": round(segment.end, 2),
                "text": segment.text.strip()
            }
        )

    output_file = (
        transcripts_folder /
        f"{video_path.stem}_transcript.json"
    )

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(
            transcript_data,
            file,
            indent=4,
            ensure_ascii=False
        )

    return output_file

if __name__ == "__main__":
    settings = load_settings()

    video_files = get_video_files(settings)

    if not video_files:
        print("No videos found.")
    else:
        print("Loading model...")
        model = load_model(settings)

        for video_file in video_files:
            print(f"\nProcessing: {video_file.name}")

            transcript_file = (
            Path(__file__).parent.parent /
            settings["transcripts_folder"].replace("../", "") /
            f"{video_file.stem}_transcript.json"
            )

            if transcript_file.exists():
                print("Transcript already exists. Skipping.")
                continue

            segments, info = transcribe_video(
                model,
                video_file
            )

            output_file = save_transcript(
                video_file,
                segments,
                info,
                settings
            )

            print(f"Saved transcript: {output_file}")