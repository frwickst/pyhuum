from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    huum_username: Optional[str] = None
    huum_password: Optional[str] = None


settings = Settings()
