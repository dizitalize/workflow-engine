from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Workflow Engine"
    app_env: str = "development"
    log_level: str = "INFO"

    database_url: str = "sqlite:///data/workflow.db"
    database_echo: bool = False

    api_host: str = "127.0.0.1"
    api_port: int = 8000

    default_timeout: int = 30


settings = Settings()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)