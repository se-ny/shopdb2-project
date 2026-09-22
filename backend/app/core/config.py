from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str

    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    openai_api_key: str | None = None
    gemini_api_key: str | None = None
    
    jwt_secret_key: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24  # 24시간
    redis_url: str = "redis://localhost:6379/0"
    refund_delay_alert_days: int = 3  # 이 기간 넘게 REQUESTED/REVIEWING 상태면 지연 알림
    

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()