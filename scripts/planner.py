import json
from pathlib import Path

import google.generativeai as genai

def load_settings():
    """
    Load project configuration from settings.json.
    """

    config_path = Path(__file__).parent.parent / "config" / "settings.json"

    with open(config_path, "r", encoding="utf-8") as file:
        settings = json.load(file)

    return settings

def load_secrets():
    """
    Load secrets from secrets.json.
    """

    secrets_path = (
        Path(__file__).parent.parent /
        "config" /
        "secrets.json"
    )

    with open(secrets_path, "r", encoding="utf-8") as file:
        secrets = json.load(file)

    return secrets

def load_planner_prompt():
    """
    Load planner prompt from planner_prompt.txt.
    """

    prompt_path = (
        Path(__file__).parent.parent /
        "config" /
        "planner_prompt.txt"
    )

    with open(prompt_path, "r", encoding="utf-8") as file:
        prompt = file.read()

    return prompt

def configure_gemini(secrets):
    """
    Configure Gemini API.
    """

    genai.configure(
        api_key=secrets["gemini_api_key"]
    )

    model = genai.GenerativeModel(
        "gemini-2.5-flash"
    )

    return model

def generate_editing_plan(
    model,
    planner_prompt,
    timestamped_transcript
):
    """
    Generate an editing plan using Gemini.
    """

    full_prompt = (
        planner_prompt
        + "\n\nTIMESTAMPED TRANSCRIPT:\n\n"
        + timestamped_transcript
    )

    response = model.generate_content(
        full_prompt
    )

    return response.text

def clean_json_response(response_text):
    """
    Remove markdown code fences from Gemini output.
    """

    cleaned = response_text.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]

    return cleaned.strip()

def parse_editing_plan(response_text):
    """
    Convert Gemini response into a Python dictionary.
    """

    cleaned_json = clean_json_response(
        response_text
    )

    editing_plan = json.loads(
        cleaned_json
    )

    return editing_plan

def save_editing_plan(
    transcript_data,
    editing_plan,
    settings
):
    """
    Save editing plan JSON.
    """

    plans_folder = (
        Path(__file__).parent.parent /
        settings["plans_folder"].replace("../", "")
    )

    output_file = (
        plans_folder /
        f"{Path(transcript_data['source_file']).stem}_editing_plan.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            editing_plan,
            file,
            indent=4,
            ensure_ascii=False
        )

    return output_file

def get_transcript_files(settings):
    """
    Find all transcript JSON files.
    """

    transcripts_folder = (
        Path(__file__).parent.parent /
        settings["transcripts_folder"].replace("../", "")
    )

    transcript_files = list(
        transcripts_folder.glob("*_transcript.json")
    )

    return transcript_files

def load_transcript(transcript_file):
    """
    Load a transcript JSON file.
    """

    with open(transcript_file, "r", encoding="utf-8") as file:
        transcript_data = json.load(file)

    return transcript_data

def get_full_text(transcript_data):
    """
    Combine all transcript segments into one text block.
    """

    full_text = " ".join(
        segment["text"]
        for segment in transcript_data["segments"]
    )

    return full_text

def get_timestamped_transcript(transcript_data):
    """
    Convert transcript segments into a timestamped text block.
    """

    lines = []

    for segment in transcript_data["segments"]:
        lines.append(
            f"[{segment['start']} - {segment['end']}] "
            f"{segment['text']}"
        )

    return "\n".join(lines)

def classify_content_type(full_text):
    """
    Classify the content type from transcript text.
    """

    text = full_text.lower()

    testimonial_keywords = [
        "amazing",
        "grateful",
        "thankful",
        "talented",
        "knowledgeable",
        "classes",
        "teacher",
        "joined"
    ]

    testimonial_score = sum(
        keyword in text
        for keyword in testimonial_keywords
    )

    if testimonial_score >= 3:
        return "testimonial"

    return "general"

if __name__ == "__main__":

    settings = load_settings()

    secrets = load_secrets()

    model = configure_gemini(
        secrets
    )

    planner_prompt = load_planner_prompt()

    transcript_files = get_transcript_files(
        settings
    )

    transcript_file = (
        transcript_files[0]
    )

    transcript_data = load_transcript(
        transcript_file
    )

    timestamped_transcript = (
        get_timestamped_transcript(
            transcript_data
        )
    )

    response_text = generate_editing_plan(
        model,
        planner_prompt,
        timestamped_transcript
    )

    editing_plan = parse_editing_plan(
        response_text
    )

    output_file = save_editing_plan(
        transcript_data,
        editing_plan,
        settings
    )

    print(
        f"Saved editing plan: {output_file}"
    )