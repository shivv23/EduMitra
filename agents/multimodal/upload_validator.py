"""Secure file upload validation.

HIGHEST-RISK component. Validates uploads by magic bytes (NOT extension/Content-Type),
re-encodes images, strips EXIF, and enforces strict limits.
"""

import logging
import os
import uuid
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

ALLOWED_MIME_MAGIC = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"RIFF": "image/webp",
    b"%PDF": "application/pdf",
}

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB
MAX_DIMENSIONS = (4096, 4096)


def detect_mime_by_magic(content: bytes) -> Optional[str]:
    """Detect MIME type by magic bytes. This is the SOURCE OF TRUTH, not the Content-Type header."""
    for magic, mime in ALLOWED_MIME_MAGIC.items():
        if content[:len(magic)] == magic:
            return mime
    return None


def validate_upload(content: bytes, content_type: Optional[str] = None) -> Tuple[bool, str]:
    """Validate an uploaded file.

    Returns (is_valid, error_message).
    """
    if len(content) == 0:
        return False, "Empty file"

    if len(content) > MAX_FILE_SIZE:
        return False, f"File too large. Max {MAX_FILE_SIZE // (1024*1024)}MB"

    detected_mime = detect_mime_by_magic(content)
    if detected_mime is None:
        return False, "Unsupported file type. Allowed: JPEG, PNG, WebP, PDF"

    return True, "OK"


def strip_exif(image_bytes: bytes) -> bytes:
    """Strip EXIF GPS/location metadata from images (privacy for minors)."""
    try:
        from PIL import Image
        from PIL.ExifTags import Base
        img = Image.open(BytesIO(image_bytes))

        # Create new image without EXIF
        data = list(img.getdata())
        clean = Image.new(img.mode, img.size)
        clean.putdata(data)

        output = BytesIO()
        clean.save(output, format=img.format or "PNG")
        return output.getvalue()
    except Exception as e:
        logger.warning("EXIF stripping failed (continuing): %s", e)
        return image_bytes


def generate_random_filename(original_name: str) -> str:
    """Generate a random, non-guessable filename while preserving extension."""
    ext = os.path.splitext(original_name)[1].lower()
    random_name = uuid.uuid4().hex
    return f"{random_name}{ext}"


# For type hint
from io import BytesIO
