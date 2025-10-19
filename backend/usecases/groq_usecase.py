from groq import Groq

from backend.config.settings import settings


class GroqUsecase:
    def __init__(self):
        self.groq = Groq(api_key=settings.GROQ_API_KEY)

    async def generate_response(self, prompt: str):
        response = self.groq.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
