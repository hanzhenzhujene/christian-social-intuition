from __future__ import annotations

import json
import time
from typing import Any
from urllib.request import Request, urlopen


class OllamaClient:
    def __init__(self, model: str, *, base_url: str = "http://127.0.0.1:11434", timeout: int = 120):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.0,
        max_tokens: int = 128,
        seed: int | None = None,
        retries: int = 3,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if seed is not None:
            payload["seed"] = seed

        request = Request(
            f"{self.base_url}/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        last_error: Exception | None = None
        for attempt in range(retries):
            try:
                with urlopen(request, timeout=self.timeout) as response:
                    return json.loads(response.read().decode("utf-8"))
            except Exception as exc:  # pragma: no cover - resilience path
                last_error = exc
                if attempt == retries - 1:
                    raise
                time.sleep(1.0 + attempt)
        raise RuntimeError(f"Ollama request failed: {last_error}")

    @staticmethod
    def extract_text(response: dict[str, Any]) -> str:
        return response["choices"][0]["message"]["content"]
