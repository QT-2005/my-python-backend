import logging
import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

logger = logging.getLogger(__name__)


def _build_ssl_args() -> dict:
    """Xây dựng tham số SSL cho kết nối MySQL."""
    if not settings.DB_USE_SSL:
        return {}

    ca_path = settings.DB_SSL_CA

    # Nếu có CA cert path, kiểm tra file tồn tại
    if ca_path:
        # Hỗ trợ relative path từ thư mục dự án
        if not os.path.isabs(ca_path):
            ca_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ca_path)
        if os.path.isfile(ca_path):
            logger.info("Using SSL CA certificate: %s", ca_path)
            return {"ssl": {"ca": ca_path}}
        else:
            logger.warning("SSL CA file not found at %s, falling back to default SSL", ca_path)

    # Mặc định: bật SSL xác thực bằng system CA
    logger.info("Using default system SSL (no custom CA)")
    return {"ssl": True}


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args=_build_ssl_args(),
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def init_db():
    """Tạo tất cả bảng nếu chưa tồn tại (dùng cho deployment không có migration)."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✓ Database tables created / verified successfully.")
    except Exception as e:
        logger.error("✗ Failed to create database tables: %s", e)
        raise


async def get_db() -> AsyncSession:
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()