import logging
import uuid

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from typing import List

from src.config.settings import settings
from src.schemas.common import Role

logger = logging.getLogger(__name__)
bearer_scheme = HTTPBearer(auto_error=False)

JWKS_CACHE = None

CUSTOM_ALGORITHM = "HS256"
CUSTOM_JWT_ISSUER = "edumitra-ai"


async def get_jwks() -> dict | None:
    global JWKS_CACHE
    if JWKS_CACHE is None:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(settings.supabase_jwks_url)
                resp.raise_for_status()
                JWKS_CACHE = resp.json()
        except Exception as e:
            logger.warning("JWKS fetch failed: %s", e)
            JWKS_CACHE = {}
    return JWKS_CACHE or {}


async def verify_jwt(token: str) -> dict | None:
    """Try custom JWT first, then fall back to Supabase JWKS."""
    try:
        payload = jwt.decode(token, settings.encryption_key, algorithms=[CUSTOM_ALGORITHM])
        logger.info("Custom JWT verified for user %s", payload.get("sub", "unknown"))
        return _custom_payload_to_supabase_format(payload)
    except JWTError:
        pass

    jwks = await get_jwks()
    if not jwks.get("keys"):
        return None
    try:
        unverified_header = jwt.get_unverified_header(token)
    except Exception:
        return None
    rsa_key = {}
    for key in jwks.get("keys", []):
        if key["kid"] == unverified_header["kid"]:
            rsa_key = key
            break
    if not rsa_key:
        return None
    try:
        return jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            audience="authenticated",
            options={"verify_exp": True},
        )
    except JWTError:
        return None


def _custom_payload_to_supabase_format(payload: dict) -> dict:
    return {
        "sub": payload.get("sub"),
        "email": payload.get("email", ""),
        "role": "authenticated",
        "user_metadata": {
            "name": payload.get("name", "User"),
            "role": payload.get("role", "student"),
        },
    }


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    payload = await verify_jwt(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return payload


async def get_current_user_id(current_user: dict = Depends(get_current_user)) -> str:
    return current_user.get("sub")


def require_role(allowed_roles: List[Role]):
    async def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_role = current_user.get("user_metadata", {}).get("role", "student")
        if user_role not in [r.value for r in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user_role}' not authorized. Requires: {[r.value for r in allowed_roles]}",
            )
        return current_user
    return role_checker


async def require_student(current_user: dict = Depends(require_role([Role.STUDENT]))) -> dict:
    return current_user


async def require_teacher(current_user: dict = Depends(require_role([Role.TEACHER, Role.ADMIN]))) -> dict:
    return current_user


async def require_admin(current_user: dict = Depends(require_role([Role.ADMIN]))) -> dict:
    return current_user
