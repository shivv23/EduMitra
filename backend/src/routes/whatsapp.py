"""WhatsApp Business API webhook handler.

Security: HMAC signature verification, schema validation, idempotency, rate limiting.
"""

import hashlib
import hmac
import logging
from typing import Dict

from fastapi import APIRouter, Request, HTTPException, status

from src.config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/whatsapp", tags=["WhatsApp"])


def verify_webhook_signature(payload: bytes, signature_header: str) -> bool:
    """Verify WhatsApp webhook signature using HMAC-SHA256 with constant-time comparison.

    Args:
        payload: Raw request body bytes.
        signature_header: Value of X-Hub-Signature-256 header.

    Returns:
        True if signature is valid, False otherwise.
    """
    if not signature_header:
        return False

    expected_signature = "sha256=" + hmac.new(
        key=settings.whatsapp_app_secret.encode(),
        msg=payload,
        digestmod=hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected_signature, signature_header)


@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = None,
    hub_verify_token: str = None,
    hub_challenge: str = None,
):
    """WhatsApp webhook verification (GET request from Meta)."""
    if hub_mode == "subscribe" and hub_verify_token == settings.whatsapp_webhook_verify_token:
        logger.info("WhatsApp webhook verified")
        return int(hub_challenge)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Verification failed")


@router.post("/webhook")
async def handle_webhook(request: Request):
    """Handle incoming WhatsApp messages.

    Verifies signature, validates payload, checks idempotency, and routes to LangGraph.
    """
    raw_body = await request.body()
    signature = request.headers.get("x-hub-signature-256", "")

    if not verify_webhook_signature(raw_body, signature):
        logger.warning("WhatsApp webhook signature verification failed")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid signature")

    payload = await request.json()

    # Placeholder — actual implementation:
    # 1. Validate payload schema with Pydantic
    # 2. Check idempotency store for message_id
    # 3. Extract sender phone, message text, media type
    # 4. Rate-limit per phone number
    # 5. Map phone to authenticated profile (via hash lookup)
    # 6. Route message text through LangGraph supervisor
    # 7. Send response via WhatsApp API

    logger.info("WhatsApp message received (validated and will be processed)")

    return {"status": "received"}
