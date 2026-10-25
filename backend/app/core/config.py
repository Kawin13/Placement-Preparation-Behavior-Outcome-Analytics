import json
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "Placement Preparation Behavior & Outcome Analytics"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "dev_secret_key_change_in_production_placement_analytics_2026"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/placement_portal"

    # AI Learning Coach (Optional External Provider Configuration)
    AI_PROVIDER: str = "gemini"  # "gemini" | "offline"
    GEMINI_API_KEY: Union[str, None] = None
    AI_API_KEY: Union[str, None] = None
    AI_MODEL_NAME: str = "gemini-1.5-flash"
    AI_TIMEOUT_SECONDS: int = 8

    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # Programming Code Execution Sandbox Configurations
    CODE_EXECUTION_ENABLED: bool = True
    CODE_EXECUTION_TIMEOUT_SEC: float = 3.0
    CODE_EXECUTION_MAX_OUTPUT_BYTES: int = 65536
    CODE_EXECUTION_MAX_CODE_BYTES: int = 65536

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["http://localhost:5173", "http://127.0.0.1:5173"]

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_production_secret(cls, v: str, info) -> str:
        # In production, require strong secrets that are not default dev keys
        if "dev_secret_key" in v and info.data.get("ENVIRONMENT") == "production":
            raise ValueError("Production environment requires an explicitly set, strong SECRET_KEY.")
        return v


settings = Settings()
