import asyncio
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from src.config.settings import settings
from src.middleware.security import configure_security_middleware
from src.middleware.logging import configure_logging
from src.routes.whatsapp import router as whatsapp_router
from src.routes.data_protection import router as data_protection_router

# Add workspace root to path so agents/ is importable
_hackarena = Path(__file__).resolve().parent.parent.parent
if str(_hackarena) not in sys.path:
    sys.path.insert(0, str(_hackarena))

from src.routes.api import router as api_router
from src.auth.routes import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: warm caches, seed vector store."""
    try:
        import os
        os.environ["CHROMA_DB_PATH"] = str(_hackarena / settings.chroma_db_path)

        # Pre-warm JWKS cache so first request isn't slow
        from src.auth.dependencies import get_jwks
        await get_jwks()
        logger.info("JWKS cache warmed")

        # Seed vector store (runs in thread to avoid blocking)
        from agents.rag.vector_store import seed_curriculum
        count = await asyncio.to_thread(seed_curriculum)
        logger.info("Vector store ready: %d chunks", count)

        # Pre-import heavy modules so they're loaded before first request
        import httpx
        _ = httpx.AsyncClient()
        logger.info("HTTPX client pre-loaded")
    except Exception as e:
        logger.warning("Startup warmup partial: %s", e)
    yield


import logging
logger = logging.getLogger(__name__)

app = FastAPI(
    title="EduMitra AI",
    description="Multi-Agent Personalized Learning + Mental Wellness Companion",
    version="0.1.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

configure_security_middleware(app)
configure_logging()

app.include_router(auth_router)
app.include_router(whatsapp_router)
app.include_router(data_protection_router)
app.include_router(api_router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
