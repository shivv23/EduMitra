"""Self-contained auth endpoints — signup, signin, me."""
import hashlib
import json
import logging
import os
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt, JWTError
from pydantic import BaseModel, EmailStr, Field

from src.auth.dependencies import get_current_user, get_current_user_id
from src.config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["Auth"])

USER_DB_PATH = os.path.join(os.path.dirname(__file__), "users.json")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30


def _hash_password(password: str) -> str:
    salt = os.urandom(32)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return salt.hex() + ":" + dk.hex()


def _verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, dk_hex = stored.split(":", 1)
        salt = bytes.fromhex(salt_hex)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
        return dk.hex() == dk_hex
    except (ValueError, AttributeError):
        return False


def _load_users() -> dict:
    if not os.path.exists(USER_DB_PATH):
        return {}
    try:
        with open(USER_DB_PATH) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_users(users: dict):
    with open(USER_DB_PATH, "w") as f:
        json.dump(users, f, indent=2)


def _sign_jwt(user_id: str, user_data: dict) -> str:
    payload = {
        "sub": user_id,
        "email": user_data["email"],
        "name": user_data.get("name", ""),
        "role": user_data.get("role", "student"),
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS),
    }
    return jwt.encode(payload, settings.encryption_key, algorithm=ALGORITHM)


def verify_custom_jwt(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.encryption_key, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    name: str = Field(..., min_length=1, max_length=100)
    role: str = Field(default="student", pattern=r"^(student|teacher|parent|admin)$")


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    token: str
    user: dict


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(req: SignUpRequest):
    users = _load_users()
    email_key = req.email.lower().strip()
    if email_key in users:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    user_id = str(uuid.uuid4())
    users[email_key] = {
        "id": user_id,
        "email": email_key,
        "name": req.name.strip(),
        "role": req.role,
        "password_hash": _hash_password(req.password),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _save_users(users)
    token = _sign_jwt(user_id, users[email_key])
    return AuthResponse(
        token=token,
        user={"id": user_id, "email": email_key, "name": req.name.strip(), "role": req.role},
    )


@router.post("/signin", response_model=AuthResponse)
async def signin(req: SignInRequest):
    users = _load_users()
    email_key = req.email.lower().strip()
    record = users.get(email_key)
    if not record or not _verify_password(req.password, record["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    token = _sign_jwt(record["id"], record)
    return AuthResponse(
        token=token,
        user={"id": record["id"], "email": email_key, "name": record["name"], "role": record["role"]},
    )


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "id": current_user.get("sub"),
        "email": current_user.get("email", ""),
        "name": current_user.get("name", ""),
        "role": current_user.get("user_metadata", {}).get("role", current_user.get("role", "student")),
    }
