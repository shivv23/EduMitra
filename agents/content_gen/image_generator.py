"""Image generation via Stability AI API (Stable Diffusion).

Generates educational diagrams, concept illustrations, and mind maps
for Indian curriculum topics. All prompts sanitized through ContentSafetyFilter.
"""

import base64
import logging
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)

STABILITY_API_URL = "https://api.stability.ai/v2beta/stable-image/generate/sd3"


async def generate_image(
    prompt: str,
    negative_prompt: str = "",
    aspect_ratio: str = "1:1",
    output_format: str = "png",
    style_preset: str = "digital-art",
    cfg_scale: float = 7.0,
) -> Dict[str, Any]:
    """Generate an image using Stability AI's Stable Diffusion 3.

    Args:
        prompt: Text description of the image to generate.
        negative_prompt: Things to avoid in the image.
        aspect_ratio: Aspect ratio (e.g. '1:1', '16:9', '4:3').
        output_format: Output image format ('png', 'jpeg', 'webp').
        style_preset: Style preset for generation.
        cfg_scale: How closely to follow the prompt (0-30, default 7).

    Returns:
        Dict with 'image_base64' and 'seed', or 'error' on failure.
    """
    from src.config.settings import settings

    api_key = settings.stable_diffusion_api_key
    if not api_key or api_key == "placeholder":
        return {"error": "Stable Diffusion API key not configured.", "success": False}

    from agents.content_gen.generator import ContentSafetyFilter
    if not ContentSafetyFilter.is_safe_prompt(prompt):
        return {"error": "Cannot generate image for this topic.", "success": False}

    payload = {
        "prompt": prompt,
        "output_format": output_format,
        "aspect_ratio": aspect_ratio,
        "style_preset": style_preset,
        "cfg_scale": cfg_scale,
    }
    if negative_prompt:
        payload["negative_prompt"] = negative_prompt

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                STABILITY_API_URL,
                headers={
                    "authorization": f"Bearer {api_key}",
                    "accept": "image/*",
                },
                data=payload,
            )
            if resp.status_code == 200:
                image_b64 = base64.b64encode(resp.content).decode("utf-8")
                seed = resp.headers.get("seed", "0")
                return {
                    "image_base64": image_b64,
                    "seed": seed,
                    "content_type": resp.headers.get("content-type", f"image/{output_format}"),
                    "success": True,
                }
            else:
                error_body = resp.text[:500]
                logger.error("Stability API error %d: %s", resp.status_code, error_body)
                return {"error": f"Image generation API error: {resp.status_code}", "success": False}
    except Exception as e:
        logger.error("Image generation failed: %s", e)
        return {"error": f"Image generation failed: {str(e)}", "success": False}
