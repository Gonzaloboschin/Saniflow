from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de la aplicación, leída de variables de entorno / .env"""

    app_name: str = "SaniFlow API"
    environment: str = "development"
    database_url: str = "postgresql+psycopg2://saniflow:saniflow@localhost:5432/saniflow"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Notificaciones por mail. Si smtp_host/smtp_user/smtp_password quedan
    # vacíos, el sistema simplemente no envía nada — no rompe la creación
    # de trabajos por no tener esto configurado.
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_name: str = "SaniFlow"
    admin_emails: str = ""  # separados por coma, ej: "a@x.com,b@x.com"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def admin_emails_list(self) -> list[str]:
        return [e.strip() for e in self.admin_emails.split(",") if e.strip()]


settings = Settings()
