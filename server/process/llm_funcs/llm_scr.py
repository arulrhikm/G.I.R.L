# Groq LLM with conversation history
import yaml
import json
import os
from pathlib import Path
from groq import Groq

# Get the project root directory
# llm_scr.py -> llm_funcs -> process -> server -> G.I.R.L (project root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
CONFIG_PATH = PROJECT_ROOT / 'character_config.yaml'

with open(CONFIG_PATH, 'r') as f:
    char_config = yaml.safe_load(f)

client = Groq(api_key=char_config['GROQ_API_KEY'])

# Constants
HISTORY_FILE = char_config['history_file']
MODEL = char_config['model']
SYSTEM_MESSAGE = {
    "role": "system",
    "content": char_config['presets']['default']['system_prompt']
}

# Load/save chat history
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return [SYSTEM_MESSAGE]

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def get_riko_response(messages):
    """Call Groq API with conversation history"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=1,
        max_tokens=2048,
    )
    return response.choices[0].message.content


def llm_response(user_input):
    messages = load_history()

    # Append user message
    messages.append({
        "role": "user",
        "content": user_input
    })

    # Get response from Groq
    assistant_response = get_riko_response(messages)

    # Append assistant message
    messages.append({
        "role": "assistant",
        "content": assistant_response
    })

    save_history(messages)
    return assistant_response


if __name__ == "__main__":
    # Quick test
    print(llm_response("Hello, who are you?"))