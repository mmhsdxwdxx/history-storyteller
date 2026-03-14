import httpx
from .base import AIProvider

class GeminiProvider(AIProvider):
    def __init__(self, api_url: str, api_key: str, model: str):
        self.api_url = api_url
        self.api_key = api_key
        self.model = model

    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        async with httpx.AsyncClient() as client:
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

            response = await client.post(
                f"{self.api_url}/v1beta/models/{self.model}:generateContent",
                headers={"x-goog-api-key": self.api_key},
                json={"contents": [{"parts": [{"text": full_prompt}]}]},
                timeout=60.0
            )
            response.raise_for_status()
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
