"""BhashaMitra Agent — real-time STT and TTS in Indian languages via Sarvam AI.

Transcribed text is treated as UNTRUSTED and routed through the prompt-injection sanitizer.
"""

import logging
import os
from typing import Any, Dict

import httpx

logger = logging.getLogger(__name__)

# Try the backend settings object first (preferred), fall back to os.getenv.
# The settings object is typically loaded when running inside the FastAPI app.
try:
    from src.config.settings import settings as _s

    SARVAM_BASE_URL = _s.sarvam_base_url
    SARVAM_API_KEY = _s.sarvam_api_key
except (ImportError, Exception):
    SARVAM_BASE_URL = os.getenv("SARVAM_BASE_URL", "https://api.sarvam.ai")
    SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")

SARVAM_LANG_MAP = {
    "hi": "hi-IN", "ta": "ta-IN", "te": "te-IN", "bn": "bn-IN",
    "mr": "mr-IN", "gu": "gu-IN", "kn": "kn-IN", "ml": "ml-IN",
    "pa": "pa-IN", "ur": "ur-IN", "en": "en-IN",
}


def _headers() -> Dict[str, str]:
    return {
        "api-subscription-key": SARVAM_API_KEY,
    }


async def transcribe_audio(audio_data: bytes, language: str = "hi") -> Dict[str, Any]:
    """Transcribe audio using Sarvam AI STT.

    Args:
        audio_data: Raw audio bytes (validated, re-encoded).
        language: Language code (e.g., 'hi', 'ta', 'te').

    Returns:
        Dict with 'transcript' and 'language_detected'.
    """
    logger.info("Transcribing audio (%d bytes, lang: %s)", len(audio_data), language)

    if not SARVAM_API_KEY or SARVAM_API_KEY == "placeholder":
        raise ValueError("SARVAM_API_KEY not set")

    lang_code = SARVAM_LANG_MAP.get(language, "hi-IN")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            files = {"file": ("audio.wav", audio_data, "audio/wav")}
            data = {"language_code": lang_code, "model": "saaras:v3", "mode": "transcribe"}
            resp = await client.post(
                f"{SARVAM_BASE_URL}/speech-to-text",
                headers=_headers(),
                data=data,
                files=files,
            )
            resp.raise_for_status()
            result = resp.json()
            transcript = result.get("transcript", "") or result.get("text", "")
            return {
                "transcript": transcript,
                "language_detected": result.get("language_code", lang_code),
            }
    except httpx.HTTPStatusError as e:
        logger.error("Sarvam STT API error: %s - %s", e.response.status_code, e.response.text)
        raise
    except Exception as e:
        logger.error("Sarvam STT failed: %s", e)
        raise


async def synthesize_speech(
    text: str, language: str = "hi", voice: str = "shubh"
) -> Dict[str, Any]:
    """Synthesize speech using Sarvam AI TTS.

    Args:
        text: Text to synthesize (already sanitized).
        language: Language code.
        voice: Speaker voice (e.g. 'shubh', 'priya', 'neha').

    Returns:
        Dict with 'audios' (list of base64 strings) and 'request_id'.
    """
    logger.info("Synthesizing speech (%d chars, lang: %s, voice: %s)", len(text), language, voice)

    if not SARVAM_API_KEY or SARVAM_API_KEY == "placeholder":
        raise ValueError("SARVAM_API_KEY not set")

    lang_code = SARVAM_LANG_MAP.get(language, "hi-IN")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {
                "text": text,
                "target_language_code": lang_code,
                "speaker": voice,
                "model": "bulbul:v3",
                "pace": 1.0,
                "speech_sample_rate": 22050,
            }
            resp = await client.post(
                f"{SARVAM_BASE_URL}/text-to-speech",
                headers={"api-subscription-key": SARVAM_API_KEY, "Content-Type": "application/json"},
                json=payload,
            )
            resp.raise_for_status()
            result = resp.json()
            return {
                "audios": result.get("audios", []),
                "request_id": result.get("request_id", ""),
            }
    except httpx.HTTPStatusError as e:
        logger.error("Sarvam TTS API error: %s - %s", e.response.status_code, e.response.text)
        raise
    except Exception as e:
        logger.error("Sarvam TTS failed: %s", e)
        raise


def language_code_to_name(code: str) -> str:
    """Map language code to display name."""
    languages = {
        "hi": "Hindi", "ta": "Tamil", "te": "Telugu", "bn": "Bengali",
        "mr": "Marathi", "gu": "Gujarati", "kn": "Kannada", "ml": "Malayalam",
        "pa": "Punjabi", "ur": "Urdu", "en": "English",
    }
    return languages.get(code, code)
