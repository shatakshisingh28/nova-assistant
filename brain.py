
"""Nova's fast AI brain using Groq."""
import os
import time
from openai import OpenAI

SYSTEM_PROMPT = (
    "You are Nova, a friendly personal assistant. Help with questions, "
    "planning, writing, studying, coding and everyday decisions. "
    "Keep replies concise, usually one to three sentences, unless more "
    "detail is requested. Use plain text without markdown or emojis. "
    "Be direct and honest."
)


class Brain:
    def __init__(self, model=None, max_turns=10):
        self.model = model or os.getenv(
            "GROQ_MODEL", "openai/gpt-oss-20b"
        )
        self.max_turns = max_turns
        self.history = []

        key = os.getenv("GROQ_API_KEY")
        self.client = (
            OpenAI(
                api_key=key,
                base_url="https://api.groq.com/openai/v1",
                timeout=20.0,
                max_retries=0,
            )
            if key else None
        )

    @property
    def available(self):
        return self.client is not None

    def ask(self, text):
        if not self.available:
            return (
                "My AI brain is offline. Please set GROQ_API_KEY "
                "in your terminal and restart Nova."
            )

        self.history.append({"role": "user", "content": text})
        self.history = self.history[-(self.max_turns * 2):]

        while self.history and self.history[0]["role"] != "user":
            self.history.pop(0)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *self.history,
        ]

        for attempt in range(2):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=200,
                )

                reply = (response.choices[0].message.content or "").strip()
                if not reply:
                    reply = "I don't have an answer for that."

                self.history.append(
                    {"role": "assistant", "content": reply}
                )
                return reply

            except Exception as exc:
                error = str(exc).lower()

                if attempt == 0 and (
                    "429" in error
                    or "503" in error
                    or "timeout" in error
                    or "connection" in error
                ):
                    time.sleep(1)
                    continue

                if self.history and self.history[-1]["role"] == "user":
                    self.history.pop()

                print(f"Groq error: {type(exc).__name__}: {exc}")

                if "429" in error:
                    return "Nova has reached an API usage limit. Please try again later."

                return "Nova couldn't reach the AI service. Please try again shortly."

        return "Nova is temporarily unavailable. Please try again."
