import ollama
import json
import datetime
import os

def generate_medical_note(text, model="qwen2.5:0.5b"):
    """
    Generates a structured medical note from the raw transcription using Ollama.

    Args:
        text (str): Raw transcription of patient observations.
        model (str): Ollama model to use.

    Returns:
        dict: Structured JSON object.
    """

    prompt = f"""
    You are an AI Medical Scribe. Convert the following raw patient observation into a structured JSON medical record.
    The output must contain exactly these keys: "subjective", "objective", "assessment", "plan", "icd_codes".
    Do not include any preamble or markdown formatting, just the raw JSON.

    Raw Observation:
    {text}
    """

    print(f"Sending request to Ollama ({model})...")

    try:
        # keep_alive=0 to unload immediately
        response = ollama.chat(
            model=model,
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0.2},
            keep_alive=0
        )

        content = response['message']['content']
        print("Response received from Ollama.")

        # Cleaning up potential markdown code blocks
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "")
        elif content.startswith("```"):
            content = content.replace("```", "")

        data = json.loads(content.strip())

        # Save to file
        save_patient_record(data)

        return data

    except Exception as e:
        print(f"Error generating medical note: {e}")
        return {}

def save_patient_record(data):
    """Saves the patient record to a JSON file."""
    directory = "patient_records"
    if not os.path.exists(directory):
        os.makedirs(directory)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{directory}/{timestamp}.json"

    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

    print(f"Record saved to {filename}")
