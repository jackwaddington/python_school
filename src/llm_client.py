import sys

import requests


class LLMClient:

    def __init__(self, host, model):
        self.host = host
        self.model = model


    def generate(self, prompt):
        url = f"http://{self.host}/api/chat"
        payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a data generator. Reply only with the exact data requested. No explanations, no numbering, no bullet points, no extra text."},
                    {"role": "user", "content": prompt}
                ],
                "stream": False
        }
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            return response.json()["message"]["content"]
        except requests.exceptions.ConnectionError:
            print(f"\nError: Could not connect to Ollama at {self.host}.")
            print("Make sure Ollama is running:  ollama serve")
            sys.exit(1)
        except Exception as e:
            print(f"\nLLM request failed: {e}")
            sys.exit(1)
