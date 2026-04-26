import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import Settings


async def test_connection():
    settings = Settings()

    print("DATABASE_URL:", settings.DATABASE_URL)

    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=True
    )

    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("Kết nối database thành công.")
            print("Kết quả test:", result.scalar())

    except Exception as e:
        print("Kết nối database thất bại.")
        print("Lỗi:", type(e).__name__)
        print(e)

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_connection())