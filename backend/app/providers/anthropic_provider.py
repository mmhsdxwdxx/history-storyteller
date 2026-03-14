import httpx
from .base import AIProvider

class AnthropicProvider(AIProvider):
    def __init__(self, api_url: str, api_key: str, model: str):
        self.api_url = api_url
        self.api_key = api_key
        self.model = model

    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        async with httpx.AsyncClient() as client:
            payload = {
                "model": self.model,
                "max_tokens": 4096,
                "messages": [{"role": "user", "content": prompt}]
            }
            if system_prompt:
                payload["system"] = system_prompt

            response = await client.post(
                f"{self.api_url}/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01"
                },
                json=payload,
                timeout=60.0
            )
            response.raise_for_status()
            return response.json()["content"][0]["text"]
