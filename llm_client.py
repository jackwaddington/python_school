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
        response = requests.post(url, json=payload)

        return response.json()["message"]["content"]
