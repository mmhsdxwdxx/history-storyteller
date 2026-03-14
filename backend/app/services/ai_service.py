from app.config import settings
from app.providers.openai_provider import OpenAIProvider
from app.providers.anthropic_provider import AnthropicProvider
from app.providers.gemini_provider import GeminiProvider

class AIService:
    def __init__(self):
        self.providers = {}

        if settings.OPENAI_API_URL and settings.OPENAI_API_KEY:
            self.providers["openai"] = OpenAIProvider(
                settings.OPENAI_API_URL,
                settings.OPENAI_API_KEY,
                settings.OPENAI_MODEL
            )

        if settings.ANTHROPIC_API_URL and settings.ANTHROPIC_API_KEY:
            self.providers["anthropic"] = AnthropicProvider(
                settings.ANTHROPIC_API_URL,
                settings.ANTHROPIC_API_KEY,
                settings.ANTHROPIC_MODEL
            )

        if settings.GEMINI_API_URL and settings.GEMINI_API_KEY:
            self.providers["gemini"] = GeminiProvider(
                settings.GEMINI_API_URL,
                settings.GEMINI_API_KEY,
                settings.GEMINI_MODEL
            )

    async def translate_to_vernacular(self, original_text: str, provider: str = None) -> str:
        if not provider:
            if settings.DEFAULT_PROVIDER and settings.DEFAULT_PROVIDER in self.providers:
                provider = settings.DEFAULT_PROVIDER
            elif len(self.providers) > 0:
                provider = list(self.providers.keys())[0]
            else:
                raise ValueError("No AI providers configured")

        if provider not in self.providers:
            available = list(self.providers.keys())
            raise ValueError(f"Provider '{provider}' not configured. Available providers: {available}")

        system_prompt = "你是一位精通古文的历史学者，擅长将文言文翻译成现代白话文。"
        prompt = f"请将以下史书原文翻译成通俗易懂的白话文：\n\n{original_text}"
        return await self.providers[provider].generate(prompt, system_prompt)

    async def create_humorous_version(self, vernacular_text: str, provider: str = None) -> str:
        if not provider:
            if settings.DEFAULT_PROVIDER and settings.DEFAULT_PROVIDER in self.providers:
                provider = settings.DEFAULT_PROVIDER
            elif len(self.providers) > 0:
                provider = list(self.providers.keys())[0]
            else:
                raise ValueError("No AI providers configured")

        if provider not in self.providers:
            available = list(self.providers.keys())
            raise ValueError(f"Provider '{provider}' not configured. Available providers: {available}")

        system_prompt = "你是一位幽默风趣的历史故事讲述者，擅长用诙谐的语言、大白话和适当的添油加醋来讲述历史故事，让内容更吸引人。"
        prompt = f"请将以下白话文改写成诙谐有趣、适合小红书发布的文稿：\n\n{vernacular_text}"
        return await self.providers[provider].generate(prompt, system_prompt)

ai_service = AIService()
