"""Multimodal Agent — image analysis and text extraction via Grok Vision (xAI).

Security: never accepts user-supplied URLs; images are always server-side stored objects.
"""

import logging
from typing import Any, Dict, Optional

from agents.llm import groq_chat_with_images

logger = logging.getLogger(__name__)

_VISION_SYSTEM_PROMPT = (
    "You are an AI assistant that analyzes images for educational purposes. "
    "The image contains handwritten notes, diagrams, or textbook content from an Indian student. "
    "Describe what you see, extract any text content, and provide a helpful summary. "
    "If the content is in Hindi or another Indian language, respond in that language. "
    "Be concise and educational. Do NOT include HTML in your response."
)


async def analyze_image(image_bytes: bytes, mime_type: str = "image/jpeg") -> Dict[str, Any]:
    """Analyze an image (handwritten notes, textbook, diagram) and return analysis + summary.

    Args:
        image_bytes: Raw image bytes (JPEG, PNG, or WebP).
        mime_type: MIME type of the image.

    Returns:
        Dict with 'analysis' (detailed) and 'summary' (short) keys.
    """
    logger.info("Analyzing image: %d bytes, type=%s", len(image_bytes), mime_type)

    try:
        full_text = await groq_chat_with_images(
            prompt="Analyze this educational image. Extract all text and describe any diagrams.",
            images=[(image_bytes, mime_type)],
            system_prompt=_VISION_SYSTEM_PROMPT,
            max_tokens=1000,
            temperature=0.3,
            model="llama-3.3-70b-versatile",
        )
        if not full_text:
            full_text = ""

        summary = await groq_chat_with_images(
            prompt=f"Summarize this in 2-3 sentences:\n\n{full_text}",
            images=[],
            max_tokens=200,
            temperature=0.2,
            model="llama-3.3-70b-versatile",
        )
        summary = summary.strip() if summary else full_text[:200]

        return {
            "analysis": full_text,
            "summary": summary,
        }
    except Exception as e:
        logger.error("Image analysis failed: %s", e)
        return {
            "analysis": f"Image analysis encountered an issue: {str(e)}",
            "summary": "Could not analyze the image. Please try again with a clearer image.",
        }


async def extract_text_from_image(image_bytes: bytes, mime_type: str = "image/jpeg") -> Optional[str]:
    """Extract text from an image using OCR via Gemini Vision.

    Args:
        image_bytes: Raw image bytes.
        mime_type: MIME type of the image.

    Returns:
        Extracted text, or None if extraction fails.
    """
    logger.info("Extracting text from image: %d bytes", len(image_bytes))

    try:
        text = await groq_chat_with_images(
            prompt="Extract all text from this image. Preserve the original language. Output only the extracted text.",
            images=[(image_bytes, mime_type)],
            max_tokens=2000,
            temperature=0.1,
            model="llama-3.3-70b-versatile",
        )
        return text.strip() if text else None
    except Exception as e:
        logger.error("Text extraction failed: %s", e)
        return None
