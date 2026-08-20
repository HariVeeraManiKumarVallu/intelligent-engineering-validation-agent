from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


def get_openrouter_llm() -> ChatOpenAI:
    """Create the Nemotron LLM client using the OpenRouter API."""

    api_key = os.getenv("OPENROUTER_NEMOTRON_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENROUTER_NEMOTRON_API_KEY is not configured."
        )

    return ChatOpenAI(
        model=os.getenv(
            "NEMOTRON_MODEL",
            "nvidia/nemotron-3.5-lightning:free",
        ),
        temperature=0,
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )


def invoke_llm(prompt: str) -> Any:
    """
    Invoke the Nemotron model through OpenRouter.

    This project uses a single LLM provider/model path.
    There is no Gemini fallback.
    """

    llm = get_openrouter_llm()

    return llm.invoke(prompt)