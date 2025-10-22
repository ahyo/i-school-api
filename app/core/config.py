from pydantic import BaseModel, EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_nama: str = "SI Sekolah"
    app_env: str = "dev"
    secret_key: str
    access_token_expire_minutes: int = 120
    database_url: str
    email_sender: EmailStr
    email_sender_name: str = "SI Sekolah"
    base_url: str = "http://localhost:8000"
    timezone: str = "Asia/Jakarta"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()
