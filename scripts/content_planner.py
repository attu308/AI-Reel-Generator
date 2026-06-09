import json
from pathlib import Path

import google.generativeai as genai


def load_secrets():

    secrets_path = (
        Path(__file__).parent.parent
        / "config"
        / "secrets.json"
    )

    with open(
        secrets_path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(
            file
        )


def load_library_summary():

    summary_path = (
        Path(__file__).parent.parent
        / "data"
        / "library_summary.txt"
    )

    with open(
        summary_path,
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


def configure_gemini(
    secrets
):

    genai.configure(
        api_key=secrets[
            "gemini_api_key"
        ]
    )

    return genai.GenerativeModel(
        "gemini-2.5-flash"
    )

def clean_json_response(
    response_text
):
    """
    Remove markdown code fences.
    """

    cleaned = (
        response_text.strip()
    )

    if cleaned.startswith(
        "```json"
    ):
        cleaned = cleaned[7:]

    if cleaned.endswith(
        "```"
    ):
        cleaned = cleaned[:-3]

    return cleaned.strip()

def save_reel_plan(
    reel_plan
):
    """
    Save reel plan JSON.
    """

    data_folder = (
        Path(__file__).parent.parent
        / "data"
    )

    output_file = (
        data_folder
        / "reel_plan.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            reel_plan,
            file,
            indent=4,
            ensure_ascii=False
        )

    return output_file

if __name__ == "__main__":

    secrets = load_secrets()

    model = configure_gemini(
        secrets
    )

    library_summary = (
        load_library_summary()
    )

    prompt_path = (
        Path(__file__).parent.parent
        / "config"
        / "content_planner_prompt.txt"
    )

    with open(
        prompt_path,
        "r",
        encoding="utf-8"
    ) as file:

        planner_prompt = (
            file.read()
        )

    prompt = (
        planner_prompt
        +
        "\n\nAVAILABLE SEGMENTS:\n\n"
        +
        library_summary
    )

    response = (
        model.generate_content(
            prompt
        )
    )

    response_text = (
        clean_json_response(
            response.text
        )
    )

    reel_plan = json.loads(
        response_text
    )

    output_file = (
        save_reel_plan(
            reel_plan
        )
    )

    print(
        f"Saved: {output_file}"
    )

    print(
        json.dumps(
            reel_plan,
            indent=4
        )
    )