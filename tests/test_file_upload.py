import pytest
from agents.multimodal.upload_validator import (
    detect_mime_by_magic,
    validate_upload,
    generate_random_filename,
)


class TestFileUploadValidation:
    def test_jpeg_detected_by_magic(self):
        content = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01"
        mime = detect_mime_by_magic(content)
        assert mime == "image/jpeg"

    def test_png_detected_by_magic(self):
        content = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
        mime = detect_mime_by_magic(content)
        assert mime == "image/png"

    def test_webp_detected_by_magic(self):
        content = b"RIFF\x00\x00\x00\x00WEBPVP8 "
        mime = detect_mime_by_magic(content)
        assert mime == "image/webp"

    def test_pdf_detected_by_magic(self):
        content = b"%PDF-1.4\n%"
        mime = detect_mime_by_magic(content)
        assert mime == "application/pdf"

    def test_txt_rejected(self):
        content = b"This is just text"
        mime = detect_mime_by_magic(content)
        assert mime is None

    def test_exe_rejected(self):
        content = b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00"
        mime = detect_mime_by_magic(content)
        assert mime is None

    def test_empty_file_rejected(self):
        valid, msg = validate_upload(b"")
        assert valid is False

    def test_valid_png_accepted(self):
        # Minimal valid PNG
        content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        valid, msg = validate_upload(content)
        assert valid is True

    def test_generated_filename_no_path_traversal(self):
        name = generate_random_filename("../../../etc/passwd")
        assert "/" not in name
        assert "\\" not in name
        assert name.endswith(".d")  # no extension in "passwd", so fallback to .d

    def test_generated_filename_preserves_extension(self):
        name = generate_random_filename("notes.png")
        assert name.endswith(".png")
        assert len(name) > 10  # uuid hex + extension


class TestExtensionSpoofing:
    """Extension spoofing attacks must be caught by magic-byte check."""

    def test_exe_renamed_to_png_rejected(self):
        # Magic bytes are MZ (EXE), but extension says .png
        content = b"MZ\x90\x00" + b"\x00" * 50
        mime = detect_mime_by_magic(content)
        assert mime is None  # Not detected as PNG despite .png extension
