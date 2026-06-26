"""Secure document ingestion for the curriculum RAG pipeline.

Only ingests from an explicit allowlist of trusted curriculum sources.
Validates and sanitizes documents before ingestion.
"""

import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Explicit allowlist of trusted curriculum sources
TRUSTED_SOURCES = {
    "ncert": {"domain": "ncert.nic.in", "type": "textbook"},
    "diksha": {"domain": "diksha.gov.in", "type": "learning_resource"},
    "epathshala": {"domain": "epathshala.nic.in", "type": "textbook"},
}

ALLOWED_FILE_EXTENSIONS = {".pdf", ".txt", ".md"}


class DocumentSource:
    def __init__(self, source_id: str, content: str, metadata: Dict):
        self.source_id = source_id
        self.content = content
        self.metadata = metadata
        self.content_hash = hashlib.sha256(content.encode()).hexdigest()


def validate_source(source_name: str) -> bool:
    """Verify the document source is in the trusted allowlist."""
    return source_name.lower() in TRUSTED_SOURCES


def sanitize_document(text: str) -> str:
    """Sanitize document content before ingestion.

    Strips potential injection vectors embedded in documents.
    """
    import re
    text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<iframe[^>]*>.*?</iframe>", "", text, flags=re.DOTALL | re.IGNORECASE)
    return text


def validate_file(path: str) -> bool:
    """Validate a file before ingestion."""
    p = Path(path)
    if not p.exists():
        logger.error("File not found: %s", path)
        return False
    if p.suffix.lower() not in ALLOWED_FILE_EXTENSIONS:
        logger.error("Unsupported file type: %s", p.suffix)
        return False
    if p.stat().st_size > 50 * 1024 * 1024:  # 50MB max
        logger.error("File too large: %s", path)
        return False
    return True


def ingest_document(
    file_path: str,
    source_name: str,
    subject: str,
    chapter: str,
    additional_metadata: Optional[Dict] = None,
) -> Optional[DocumentSource]:
    """Ingest a document into the RAG pipeline.

    Steps:
    1. Validate source is in allowlist
    2. Validate file
    3. Read and sanitize content
    4. Hash content
    5. Return DocumentSource for indexing

    Actual vector store insertion is handled by the indexing pipeline (ChromaDB/pgvector).
    """
    if not validate_source(source_name):
        logger.error("Untrusted source '%s'. Must be one of: %s", source_name, list(TRUSTED_SOURCES.keys()))
        return None

    if not validate_file(file_path):
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw_content = f.read()
    except Exception as e:
        logger.error("Failed to read file %s: %s", file_path, e)
        return None

    sanitized = sanitize_document(raw_content)

    metadata = {
        "source": source_name,
        "subject": subject,
        "chapter": chapter,
        **(additional_metadata or {}),
    }

    doc = DocumentSource(
        source_id=f"{source_name}:{subject}:{chapter}:{Path(file_path).name}",
        content=sanitized,
        metadata=metadata,
    )

    logger.info(
        "Ingested document: %s (hash: %s, size: %d chars)",
        doc.source_id,
        doc.content_hash[:16],
        len(sanitized),
    )

    return doc
