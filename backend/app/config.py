from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_DEFAULT_SECRET = "dev-secret-change-me"


class Settings(BaseSettings):
    environment: str = "dev"  # dev | prod
    database_url: str = "sqlite:///./dev.db"
    api_prefix: str = "/v1"

    # Auth — MUST set JWT_SECRET in production (the default is rejected there).
    jwt_secret: str = _DEFAULT_SECRET
    jwt_algorithm: str = "HS256"
    jwt_expire_seconds: int = 3600

    # Media storage for uploaded videos (local dir for the scaffold; S3 in prod)
    media_dir: str = "./media"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode="after")
    def _no_default_secret_in_prod(self):
        # Fail fast: never run production with the placeholder JWT secret.
        if self.environment == "prod" and self.jwt_secret == _DEFAULT_SECRET:
            raise ValueError("JWT_SECRET must be set in production (dev placeholder in use).")
        return self


settings = Settings()
