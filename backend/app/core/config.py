"""Application Configuration"""
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "CustomerLLM"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_VERSION: str = "v1"
    
    # Backend
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    BACKEND_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:3000"
    
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
    
    # Object Storage (MinIO/S3)
    S3_ENDPOINT: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_BUCKET: str = "customerllm"
    S3_SECURE: bool = False
    
    # Ollama (MVP Inference)
    OLLAMA_BASE_URL: str
    OLLAMA_MODEL: str = "jais:7b"
    OLLAMA_EMBEDDING_MODEL: str = "nomic-embed-text:latest"
    OLLAMA_TIMEOUT: int = 300
    
    # Production Inference (vLLM)
    VLLM_ENABLED: bool = False
    VLLM_BASE_URL: Optional[str] = None
    VLLM_EMBEDDING_BASE_URL: Optional[str] = None
    VLLM_MODEL: Optional[str] = None
    VLLM_API_KEY: Optional[str] = None
    
    # Embedding Configuration
    EMBEDDING_MODEL_TYPE: str = "ollama"  # ollama, vllm, openai-compatible
    EMBEDDING_MODEL_NAME: str = "nomic-embed-text:latest"
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
    UPLOAD_DIR: str = "/app/uploads"
    TEMP_DIR: str = "/tmp/customerllm"
    
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
    CORS_ORIGINS: str = Field(default="http://localhost:3000,http://localhost:5173")
    
    def get_cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string into list"""
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        return self.CORS_ORIGINS
    
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
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "env_parse_none_str": None,
        "json_schema_extra": {
            "env_parse_enums": None
        }
    }


settings = Settings()

