from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/blog"
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24h
    cors_origins: list[str] = ["http://localhost:5173"]

    model_config = {"env_prefix": "BLOG_", "env_file": ".env"}


settings = Settings()
