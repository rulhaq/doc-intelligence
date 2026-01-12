"""Application Configuration"""
from typing import List, Optional
from pydantic import Field, ValidationError, field_validator, model_validator
from pydantic_settings import BaseSettings
import structlog

logger = structlog.get_logger()

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "CustomerLLM"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str
    DEBUG: bool
    API_VERSION: str = "v1"
    
    # Backend
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int
    BACKEND_URL: str
    FRONTEND_URL: str
    
    # Database
    DATABASE_URL: str
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 40
    
    # Redis
    REDIS_URL: str
    REDIS_MAX_CONNECTIONS: int = 50
    
    # Qdrant
    QDRANT_URL: str
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION_NAME: str = "documents"
    QDRANT_TIMEOUT: int = 60
    
    # File Storage (PVC)
    STORAGE_MODE: str
    FILE_STORAGE_PATH: str
    
    # vLLM OpenAI-compatible inference (chat)
    VLLM_BASE_URL: str
    VLLM_MODEL: str
    VLLM_EMBEDDING_BASE_URL: Optional[str] = None
    VLLM_EMBEDDING_MODEL: Optional[str] = None
    VLLM_API_TOKEN: Optional[str] = None
    VLLM_TIMEOUT: int = 300
    VLLM_HEALTHCHECK_ENABLED: bool = True
    VLLM_HEALTHCHECK_STRICT: bool = True

    # Embeddings provider
    EMBEDDINGS_PROVIDER: str
    TEI_BASE_URL: Optional[str] = None
    TEI_API_TOKEN: Optional[str] = None
    TEI_TIMEOUT: int = 60
    
    # Embedding Configuration
    EMBEDDING_DIMENSION: int = 768
    EMBEDDING_BATCH_SIZE: int = 32
    MIN_SIMILARITY: float = 0.72
    
    # OCR Configuration
    OCR_WORKER_URL: str
    OCR_CONFIDENCE_THRESHOLD: float = 0.5
    OCR_LLM_CORRECTION_ENABLED: bool = True
    
    # Security & Authentication
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # OAuth2 Providers
    OAUTH_AZURE_ENABLED: bool = False
    OAUTH_AZURE_CLIENT_ID: Optional[str] = None
    OAUTH_AZURE_CLIENT_SECRET: Optional[str] = None
    OAUTH_AZURE_TENANT_ID: Optional[str] = None
    
    OAUTH_GOOGLE_ENABLED: bool = False
    OAUTH_GOOGLE_CLIENT_ID: Optional[str] = None
    OAUTH_GOOGLE_CLIENT_SECRET: Optional[str] = None
    
    OAUTH_GITHUB_ENABLED: bool = False
    OAUTH_GITHUB_CLIENT_ID: Optional[str] = None
    OAUTH_GITHUB_CLIENT_SECRET: Optional[str] = None
    
    # SAML Configuration
    SAML_ENABLED: bool = False
    SAML_IDP_METADATA_URL: Optional[str] = None
    SAML_ENTITY_ID: Optional[str] = None
    SAML_ACS_URL: Optional[str] = None
    
    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 100
    ALLOWED_EXTENSIONS: str = Field(default="pdf,docx,txt")
    
    def get_allowed_extensions_list(self) -> List[str]:
        """Parse ALLOWED_EXTENSIONS string into list"""
        if isinstance(self.ALLOWED_EXTENSIONS, str):
            return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",")]
        return self.ALLOWED_EXTENSIONS
    
    # Chunking & Embedding
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    SEMANTIC_CHUNKING_ENABLED: bool = True
    
    # Agent Configuration
    AGENT_EXECUTION_TIMEOUT: int = 300
    AGENT_MAX_CONCURRENT: int = 5
    AGENT_ISOLATED_RUNTIME: bool = True
    MCP_ENABLED: bool = True
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # CORS (stored as string, parsed to list in method)
    CORS_ORIGINS: str
    
    def get_cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string into list"""
        if isinstance(self.CORS_ORIGINS, str):
            # Browsers send the Origin header without a trailing slash. Normalize any
            # configured origins to avoid mismatches like `https://example.com/` vs
            # `https://example.com`.
            return [origin.strip().rstrip("/") for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        return self.CORS_ORIGINS

    @field_validator("EMBEDDINGS_PROVIDER")
    @classmethod
    def _validate_provider(cls, value: str):
        provider = value.lower()
        if provider not in ("vllm", "tei"):
            raise ValueError("EMBEDDINGS_PROVIDER must be 'vllm' or 'tei'")
        return provider

    @model_validator(mode="after")
    def _validate_embeddings_settings(self):
        if self.EMBEDDINGS_PROVIDER == "tei":
            if not self.TEI_BASE_URL:
                raise ValueError("TEI_BASE_URL must be set when EMBEDDINGS_PROVIDER=tei")
        if self.EMBEDDINGS_PROVIDER == "vllm":
            if not self.VLLM_EMBEDDING_BASE_URL or not self.VLLM_EMBEDDING_MODEL:
                raise ValueError("VLLM_EMBEDDING_BASE_URL and VLLM_EMBEDDING_MODEL are required when EMBEDDINGS_PROVIDER=vllm")
        return self
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE: Optional[str] = None
    
    # Monitoring
    PROMETHEUS_ENABLED: bool = True
    
    # Audit & Compliance
    AUDIT_LOG_ENABLED: bool = True
    PII_REDACTION_ENABLED: bool = False
    DATA_RETENTION_DAYS: int = 365
    
    # Feature Flags
    FEATURE_WEB_SCRAPING: bool = True
    FEATURE_EXTERNAL_CONNECTORS: bool = True
    FEATURE_MULTIMODAL: bool = False
    
    @field_validator(
        "APP_ENV",
        "BACKEND_URL",
        "FRONTEND_URL",
        "DATABASE_URL",
        "REDIS_URL",
        "QDRANT_URL",
        "STORAGE_MODE",
        "FILE_STORAGE_PATH",
        "VLLM_BASE_URL",
        "VLLM_MODEL",
        "EMBEDDINGS_PROVIDER",
        "OCR_WORKER_URL",
        "SECRET_KEY",
        "CORS_ORIGINS",
    )
    @classmethod
    def _require_non_empty(cls, value: str, info):
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValueError(f"{info.field_name} must be set")
        return value

    model_config = {
        "case_sensitive": True,
        "env_parse_none_str": None,
        "json_schema_extra": {
            "env_parse_enums": None
        }
    }


def load_settings() -> Settings:
    """Load settings and log missing environment variables before failing."""
    try:
        return Settings()
    except ValidationError as exc:
        missing = [
            ".".join(str(part) for part in err.get("loc", []))
            for err in exc.errors()
            if err.get("type") in ("missing", "value_error")
        ]
        if missing:
            logger.error("Missing required environment variables", missing=missing)
        else:
            logger.error("Invalid environment configuration", errors=exc.errors())
        raise


settings = load_settings()

