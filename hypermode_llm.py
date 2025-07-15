from langchain.llms.base import LLM
from typing import Optional, List
import requests
import os

class HypermodeLLM(LLM):
    """Custom LLM wrapper for Hypermode API."""

    model: str = os.getenv("HYPERMODE_MODEL")
    api_key: str = os.getenv("HYPERMODE_API_KEY")
    temperature: float = 0.7

    @property
    def _llm_type(self) -> str:
        return "hypermode"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": self.temperature,
            "max_tokens": 512
        }

        response = requests.post(
            "https://api.hypermode.dev/inference",
            json=payload,
            headers=headers,
            timeout=30
        )

        if response.status_code != 200:
            raise RuntimeError(f"Hypermode error: {response.text}")

        return response.json()["completion"]
