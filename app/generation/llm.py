import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:3b"


def generate_answer(prompt):

    response = requests.post(
        OLLAMA_URL,
        json={
          "model": MODEL_NAME,
          "prompt": prompt,
          "stream": False,
          "options": {
          "temperature": 0
           }
        },
        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    return data["response"]