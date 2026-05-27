import os
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_NAME: str = "LexiRise API"
    
    DEBUG: bool = False

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, v: Any) -> bool:
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes")
        return bool(v)

    # Database (Pydantic tự động lấy từ môi trường nếu có, nếu không sẽ dùng default bên dưới)
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "lexirise"

    @property
    def DATABASE_URL(self) -> str:
        # Xoá ?ssl=true vì aiomysql/pymysql không xử lý đúng kiểu string
        # Thay vào đó dùng ssl_args trong create_async_engine (xem database.py)
        return (
            f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # Đường dẫn tới CA certificate file (tải từ Aiven Console)
    # Nếu để trống, sẽ dùng SSL mặc định của hệ thống
    DB_SSL_CA: str = ""

    @property
    def DB_USE_SSL(self) -> bool:
        """Kiểm tra xem có cần SSL không (dựa vào host không phải local)"""
        host = self.DB_HOST.lower()
        return not (host == "localhost" or host == "127.0.0.1" or host.startswith("10.") or host.startswith("172.") or host.startswith("192.168."))

    # JWT
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Email (SMTP)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@lexirise.app"

    # URL frontend
    RESET_PASSWORD_URL: str = "http://localhost:3000/reset-password"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
