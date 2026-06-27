from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./dev.db"
    api_prefix: str = "/v1"

    # Auth (override JWT_SECRET in production!)
    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_seconds: int = 3600

    # Media storage for uploaded videos (local dir for the scaffold; S3 in prod)
    media_dir: str = "./media"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
