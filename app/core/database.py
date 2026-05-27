import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

logger = logging.getLogger(__name__)

import os


def _build_ssl_args() -> dict:
    """Xây dựng tham số SSL cho kết nối MySQL.

    DB_SSL_MODE:
      - disable  : không SSL
      - require  : bật SSL, không verify cert (dùng cho Aiven, Render)
      - verify-ca: verify CA cert (cần DB_SSL_CA trỏ tới file ca.pem)
      - verify-full: verify CA + hostname
    """
    if not settings.DB_USE_SSL:
        logger.info("SSL disabled")
        return {}

    import ssl as ssl_mod

    mode = settings.DB_SSL_MODE

    if mode == "require":
        # Không verify cert - chấp nhận mọi cert (cần cho Aiven nếu chưa có CA)
        ctx = ssl_mod.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl_mod.CERT_NONE
        logger.info("SSL mode: require (no certificate verification)")
        return {"ssl": ctx}

    # mode == "verify-ca" hoặc "verify-full"
    ca_path = settings.DB_SSL_CA
    if not ca_path:
        logger.warning("SSL mode is '%s' but DB_SSL_CA is empty, falling back to 'require'", mode)
        ctx = ssl_mod.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl_mod.CERT_NONE
        return {"ssl": ctx}

    # Hỗ trợ relative path từ thư mục dự án
    if not os.path.isabs(ca_path):
        ca_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ca_path)

    if not os.path.isfile(ca_path):
        logger.warning("CA cert not found at %s, falling back to 'require' mode", ca_path)
        ctx = ssl_mod.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl_mod.CERT_NONE
        return {"ssl": ctx}

    ctx = ssl_mod.create_default_context(cafile=ca_path)
    if mode == "verify-full":
        ctx.check_hostname = True
    else:
        ctx.check_hostname = False
    ctx.verify_mode = ssl_mod.CERT_REQUIRED
    logger.info("SSL mode: %s (CA: %s)", mode, ca_path)
    return {"ssl": ctx}

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