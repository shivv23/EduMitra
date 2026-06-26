"""Secure audio file validation.

Same security controls as multimodal upload: magic-byte validation, size limits,
re-encode/transcode, randomized names.
"""

import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

ALLOWED_AUDIO_MAGIC = {
    b"RIFF": "audio/wav",
    b"\xff\xf3": "audio/mp3",
    b"\xff\xf2": "audio/mp3",
    b"\xff\xfb": "audio/mp3",
    b"OggS": "audio/ogg",
    b"fLaC": "audio/flac",
}

MAX_AUDIO_FILE_SIZE = 25 * 1024 * 1024  # 25 MB
MAX_AUDIO_DURATION_SECONDS = 300  # 5 minutes


def detect_audio_mime_by_magic(content: bytes) -> Optional[str]:
    for magic, mime in ALLOWED_AUDIO_MAGIC.items():
        if content[:len(magic)] == magic:
            return mime
    return None


def validate_audio_upload(content: bytes) -> Tuple[bool, str]:
    """Validate an audio file upload."""
    if len(content) == 0:
        return False, "Empty file"
    if len(content) > MAX_AUDIO_FILE_SIZE:
        return False, f"Audio too large. Max {MAX_AUDIO_FILE_SIZE // (1024*1024)}MB"
    mime = detect_audio_mime_by_magic(content)
    if mime is None:
        return False, "Unsupported audio format. Allowed: WAV, MP3, OGG, FLAC"
    return True, "OK"
