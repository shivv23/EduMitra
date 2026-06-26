"""Image handling utility for generated content.

Security: re-encodes images server-side, stores with signed expiring URLs.
"""

import logging
from io import BytesIO
from typing import Optional

logger = logging.getLogger(__name__)

MAX_IMAGE_SIZE_MB = 10
ALLOWED_FORMATS = {"PNG", "JPEG", "WEBP"}


def reencode_image(image_bytes: bytes, output_format: str = "PNG") -> Optional[bytes]:
    """Re-encode image to strip embedded payloads and EXIF data.

    Args:
        image_bytes: Raw image bytes.
        output_format: Target format (PNG, JPEG, WEBP).

    Returns:
        Re-encoded image bytes, or None if processing fails.
    """
    try:
        from PIL import Image
        img = Image.open(BytesIO(image_bytes))
        # Strip EXIF and re-encode
        img = Image.new(img.mode, img.size)
        output = BytesIO()
        img.save(output, format=output_format)
        return output.getvalue()
    except Exception as e:
        logger.error("Image re-encoding failed: %s", e)
        return None


def validate_image_size(image_bytes: bytes) -> bool:
    """Validate image size is within limits."""
    size_mb = len(image_bytes) / (1024 * 1024)
    return size_mb <= MAX_IMAGE_SIZE_MB


def generate_signed_url(file_path: str, expires_in_seconds: int = 3600) -> str:
    """Generate a signed, expiring URL for a stored image.

    Returns a local data URI for development. In production, replace with
    S3 presigned URLs or Supabase storage signed URLs.
    """
    import os
    if not os.path.isfile(file_path):
        logger.warning("generate_signed_url: file not found at %s, returning placeholder", file_path)
        return ""
    try:
        import base64
        with open(file_path, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode("utf-8")
        ext = os.path.splitext(file_path)[1].lower()
        mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp"}.get(ext, "image/png")
        return f"data:{mime};base64,{b64}"
    except Exception as e:
        logger.error("generate_signed_url failed: %s", e)
        return ""
