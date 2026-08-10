from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de la aplicación, leída de variables de entorno / .env"""

    app_name: str = "SaniFlow API"
    environment: str = "development"
    database_url: str = "postgresql+psycopg2://saniflow:saniflow@localhost:5432/saniflow"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
