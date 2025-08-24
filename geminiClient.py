import google.generativeai as genai

class GeminiClient:
    def __init__(self, API_KEY: str, model: str = "gemini-2.5-flash"):
        genai.configure(api_key=API_KEY)
        self.model = genai.GenerativeModel(model)

    def query(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text