from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_url: str
    token_exp: int
    token_secret: str
    token_algorithm: str
    refresh_secret: str
    refresh_exp: int
    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    minio_secure: bool
    redis_url: str
    upload_dir: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
