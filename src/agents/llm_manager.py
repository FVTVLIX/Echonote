# src/agents/llm_manager.py
import openai
from src.config.settings import settings

class LLMManager:
    def __init__(self, provider: str = None):
        self.provider = provider or settings.llm_provider
        
    def generate(self, prompt: str, task_type: str = "general") -> dict:
        """
        Generic entry point for LLM generation.
        """
        if self.provider == "openai":
            return self._generate_openai(prompt)
        elif self.provider == "anthropic":
            return self._generate_anthropic(prompt)
        elif self.provider == "gemini":
            return self._generate_gemini(prompt)
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")

    def _generate_openai(self, prompt: str) -> dict:
        client = openai.OpenAI(api_key=settings.openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"} if "JSON" in prompt else None
        )
        return {
            "response": response.choices[0].message.content,
            "usage": response.usage.to_dict() if hasattr(response, "usage") else {}
        }

    def _generate_anthropic(self, prompt: str) -> dict:
        # Placeholder for Anthropic implementation
        # import anthropic
        # client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        raise NotImplementedError("Anthropic provider not yet implemented")

    def _generate_gemini(self, prompt: str) -> dict:
        # Placeholder for Gemini implementation
        # import google.generativeai as genai
        # genai.configure(api_key=settings.gemini_api_key)
        raise NotImplementedError("Gemini provider not yet implemented")
