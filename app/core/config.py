import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_NAME: str = "LexiRise API"
    DEBUG: bool = False

    # Database (Pydantic tự động lấy từ môi trường nếu có, nếu không sẽ dùng default bên dưới)
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "lexirise"

    @property
    def DATABASE_URL(self) -> str:
        # Đối với Aiven MySQL, cần thêm ?ssl=true hoặc tham số ssl_ca
        # Nếu dùng aiomysql, cách đơn giản nhất để vượt qua check SSL trên Cloud:
        return (
            f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?ssl=true"
        )

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
