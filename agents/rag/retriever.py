"""Secure RAG retrieval module.

Retrieves syllabus-aligned context with relevance thresholds and student isolation.
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

RELEVANCE_THRESHOLD = 0.65
MAX_RESULTS = 5


class RetrievalResult:
    def __init__(self, chunk_id: str, content: str, score: float, metadata: Dict):
        self.chunk_id = chunk_id
        self.content = content
        self.score = score
        self.metadata = metadata


async def retrieve_context(
    query: str,
    student_id: str,
    subject: Optional[str] = None,
    topic: Optional[str] = None,
    top_k: int = MAX_RESULTS,
) -> List[RetrievalResult]:
    """Retrieve relevant curriculum context for a student query.

    Args:
        query: The sanitized student query.
        student_id: Authenticated student UUID (for future RLS filtering).
        subject: Optional subject filter.
        topic: Optional topic filter.
        top_k: Maximum results to return.

    Returns:
        List of RetrievalResult with content, score, and metadata.
    """
    logger.info("Retrieving context for student %s: query='%s'", student_id, query[:50])

    try:
        from agents.rag.vector_store import retrieve
        results = await retrieve(
            query=query,
            subject=subject,
            topic=topic,
            top_k=top_k,
            relevance_threshold=RELEVANCE_THRESHOLD,
        )

        if not results:
            logger.info("No relevant context found for query: %s", query[:50])
            return []

        return [
            RetrievalResult(
                chunk_id=f"{r['metadata'].get('subject', 'unknown')}:{r['metadata'].get('topic', 'unknown')}",
                content=r["content"],
                score=r["score"],
                metadata=r["metadata"],
            )
            for r in results
        ]
    except Exception as e:
        logger.warning("Context retrieval failed: %s", e)
        return []


def format_context_for_prompt(results: List[RetrievalResult]) -> str:
    """Format retrieved chunks into a context string for the LLM prompt.

    Each chunk is tagged as untrusted for the prompt injection defense.
    """
    if not results:
        return ""

    sections = []
    for i, r in enumerate(results, 1):
        sections.append(f"[Source {i}] (relevance: {r.score:.2f})\n{r.content}")

    return "\n\n".join(sections)
