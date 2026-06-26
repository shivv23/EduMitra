from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Supabase (optional — self-contained JWT auth works without it)
    supabase_url: str = ""
    supabase_service_role_key: str = ""
    supabase_anon_key: str = ""
    supabase_jwks_url: str | None = None

    # Encryption
    encryption_key: str

    # LLM
    gemini_api_key: str = ""
    grok_api_key: str = ""
    claude_api_key: str
    stable_diffusion_api_key: str

    # Sarvam AI
    sarvam_api_key: str
    sarvam_base_url: str = "https://api.sarvam.ai"

    # WhatsApp (optional — placeholder until Meta verification proceeds)
    whatsapp_access_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_webhook_verify_token: str = ""
    whatsapp_app_secret: str = ""

    # Storage
    storage_bucket: str = "edumitra-uploads"
    storage_region: str = "auto"
    storage_endpoint: str = ""
    storage_access_key: str = ""
    storage_secret_key: str = ""

    # RAG / Vector Store
    chroma_db_path: str = "agents/rag/chroma_db"

    # LangSmith
    langchain_tracing_v2: bool = True
    langchain_api_key: str = ""
    langchain_project: str = "edumitra-ai"

    # Backend
    debug: bool = False
    log_level: str = "INFO"
    allowed_origins: str = "http://localhost:3000,https://edumitraai.vercel.app"
    rate_limit_per_ip: str = "60/minute"
    rate_limit_per_user: str = "300/hour"

    # Database
    database_url: str = ""

    @field_validator("supabase_jwks_url", mode="before")
    @classmethod
    def default_supabase_jwks_url(cls, v, info):
        if v:
            return v
        supabase_url = info.data.get("supabase_url")
        if supabase_url:
            return supabase_url.rstrip("/") + "/auth/v1/.well-known/jwks.json"
        return ""

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


settings = Settings()
