from pydantic import BaseModel, EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_nama: str = "Sistem Sekolah Online"
    app_env: str = "dev"
    secret_key: str
    access_token_expire_minutes: int = 120
    database_url: str
    email_sender: str = "ahyo.haryanto@gmail.com"
    email_sender_name: str = "Sistem Sekolah Online"
    base_url: str = "http://localhost:8000"
    timezone: str = "Asia/Jakarta"
    brevo_api_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()
