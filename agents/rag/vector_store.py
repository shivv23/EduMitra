"""ChromaDB vector store initialization, seeding, and collection management."""

import hashlib
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", str(Path(__file__).parent / "chroma_db"))
COLLECTION_NAME = "ncert_curriculum"
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

_client = None
_collection = None


def get_client():
    global _client
    if _client is None:
        import chromadb
        _client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    return _client


def get_collection():
    global _collection
    if _collection is None:
        client = get_client()
        try:
            _collection = client.get_collection(COLLECTION_NAME)
        except Exception:
            _collection = client.create_collection(COLLECTION_NAME)
    return _collection


def _chunk_text(text: str, max_chars: int = 512, overlap: int = 64) -> List[str]:
    """Split text into overlapping chunks at sentence boundaries."""
    import re
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks = []
    current = ""
    for sentence in sentences:
        if len(current) + len(sentence) > max_chars and current:
            chunks.append(current.strip())
            current = sentence
        else:
            if current:
                current += " " + sentence
            else:
                current = sentence
    if current.strip():
        chunks.append(current.strip())
    return chunks


def seed_curriculum(force: bool = False) -> int:
    """Seed the vector store with NCERT-based curriculum content.

    Args:
        force: If True, rebuild from scratch (delete + re-insert).

    Returns:
        Number of chunks inserted.
    """
    from agents.rag.curriculum_data import CURRICULUM_ENTRIES

    collection = get_collection()

    if not force and collection.count() > 50:
        logger.info("Vector store already seeded (%d chunks). Use force=True to rebuild.", collection.count())
        return collection.count()

    if force:
        client = get_client()
        client.delete_collection(COLLECTION_NAME)
        global _collection
        _collection = None
        collection = get_collection()

    chunks_inserted = 0
    for entry in CURRICULUM_ENTRIES:
        chunks = _chunk_text(entry["content"])
        for i, chunk in enumerate(chunks):
            chunk_id = hashlib.md5(f"{entry['subject']}:{entry['topic']}:{entry['chapter']}:{i}".encode()).hexdigest()
            metadata = {
                "subject": entry["subject"],
                "topic": entry["topic"],
                "chapter": entry["chapter"],
                "grade": str(entry.get("grade", 8)),
                "source": entry.get("source", "ncert"),
                "chunk_index": i,
            }
            collection.add(documents=[chunk], metadatas=[metadata], ids=[chunk_id])
            chunks_inserted += 1

    logger.info("Seeded %d chunks into vector store at %s", chunks_inserted, CHROMA_DB_PATH)
    return chunks_inserted


async def retrieve(
    query: str,
    subject: Optional[str] = None,
    topic: Optional[str] = None,
    top_k: int = 5,
    relevance_threshold: float = 0.65,
) -> List[Dict[str, Any]]:
    """Retrieve relevant curriculum chunks for a query.

    Args:
        query: The student's question.
        subject: Optional subject filter.
        topic: Optional topic filter.
        top_k: Max results to return.
        relevance_threshold: Minimum similarity score (0-1).

    Returns:
        List of dicts with content, score, and metadata.
    """
    collection = get_collection()

    where = {}
    if subject:
        where["subject"] = subject
    if topic:
        where["topic"] = topic

    try:
        results = collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where or None,
        )
    except Exception as e:
        logger.warning("ChromaDB query failed: %s", e)
        return []

    if not results or not results["documents"] or not results["documents"][0]:
        return []

    retrieved = []
    docs = results["documents"][0]
    distances = results["distances"][0] if results.get("distances") else [1.0] * len(docs)
    metadatas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)

    for doc, dist, meta in zip(docs, distances, metadatas):
        # ChromaDB uses L2 distance; convert to similarity score
        score = 1.0 / (1.0 + dist)
        if score >= relevance_threshold:
            retrieved.append({
                "content": doc,
                "score": round(score, 3),
                "metadata": meta,
            })

    return retrieved
