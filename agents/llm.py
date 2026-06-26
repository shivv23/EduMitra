"""Shared LLM client helpers for EduMitra agents.

Loads API keys from environment or .env file once at import time.
Supports Groq, Claude (Anthropic), and Gemini (Google).
"""

import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_loaded = False


def _ensure_env():
    global _loaded
    if _loaded:
        return
    candidates = [
        Path.cwd() / ".env",
        Path(__file__).resolve().parent.parent / ".env",
        Path(__file__).resolve().parent.parent.parent / ".env",
    ]
    for p in candidates:
        if p.exists():
            try:
                from dotenv import load_dotenv
                load_dotenv(p, override=False)
                logger.info("Loaded env from %s", p)
                break
            except Exception:
                pass
    _loaded = True


def get_gemini_key() -> str:
    _ensure_env()
    return os.environ.get("GEMINI_API_KEY", "placeholder")


def get_gemini_client():
    from google import genai
    key = get_gemini_key()
    return genai.Client(api_key=key)


def get_gemini_model(model: str = "gemini-2.5-flash-lite") -> str:
    return model


def get_claude_key() -> str:
    _ensure_env()
    return os.environ.get("CLAUDE_API_KEY", "placeholder")


def get_claude_client():
    from anthropic import Anthropic
    key = get_claude_key()
    return Anthropic(api_key=key)


async def claude_chat(
    message: str,
    system_prompt: str = "You are EduMitra, an AI tutor for Indian students.",
    max_tokens: int = 1024,
    temperature: float = 0.5,
) -> str:
    try:
        client = get_claude_client()
        msg = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": message}],
        )
        return msg.content[0].text if msg.content else ""
    except Exception as e:
        logger.warning("Claude chat failed: %s", e)
        return ""


def get_groq_key() -> str:
    _ensure_env()
    return os.environ.get("GROK_API_KEY", "placeholder")


def get_groq_client():
    from openai import AsyncOpenAI
    key = get_groq_key()
    return AsyncOpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")


async def groq_chat(
    message: str,
    system_prompt: str = "",
    history: list | None = None,
    max_tokens: int = 1024,
    temperature: float = 0.5,
    model: str = "llama-3.3-70b-versatile",
) -> str:
    """Send a chat message to Groq and return the response text."""
    try:
        client = get_groq_client()
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if history:
            for msg in history[-20:]:
                role = "assistant" if msg.get("role") in ("model", "assistant") else "user"
                messages.append({"role": role, "content": msg.get("content", "")})
        messages.append({"role": "user", "content": message})

        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        logger.error("Groq chat failed: %s", e)
        return ""


async def groq_chat_with_images(
    prompt: str,
    images: list[tuple[bytes, str]],
    system_prompt: str = "",
    max_tokens: int = 1024,
    temperature: float = 0.3,
    model: str = "llama-3.3-70b-versatile",
) -> str:
    """Send a message with images to Groq and return the response text."""
    try:
        import base64
        client = get_groq_client()
        messages = []
        content: list[dict] = [{"type": "text", "text": prompt}]
        for image_bytes, mime_type in images:
            b64 = base64.b64encode(image_bytes).decode("utf-8")
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:{mime_type};base64,{b64}"},
            })
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": content})

        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        logger.error("Grok vision chat failed: %s", e)
        return ""
