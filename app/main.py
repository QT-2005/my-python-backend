from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import create_tables, check_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=" * 50)
    print(f"  {settings.PROJECT_NAME}")
    print("=" * 50)

    ok = check_connection()
    if not ok:
        print("⚠️  Server vẫn khởi động nhưng database chưa kết nối được.")
        print("   Kiểm tra lại MYSQL_PASSWORD trong file .env")

    # 2. Tạo bảng nếu chưa có
    try:
        create_tables()
    except Exception as e:
        print(f"⚠️  Không thể tạo bảng: {e}")

    # 3. Seed dữ liệu mẫu
    try:
        from app.core.seed import seed_words
        from app.core.database import SessionLocal
        db = SessionLocal()
        seed_words(db)
        db.close()
    except Exception as e:
        print(f"⚠️  Seed thất bại: {e}")

    print(f"🚀 Server đang chạy tại http://{settings.HOST}:{settings.PORT}")
    print(f"📖 Swagger docs: http://127.0.0.1:{settings.PORT}/docs")
    print("=" * 50)

    yield

    print("Server đang tắt...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API từ điển Anh-Việt với phiên âm IPA",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký router
from app.routers.word import router as word_router
app.include_router(word_router)


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": f"{settings.PROJECT_NAME} đang chạy",
        "docs": "/docs",
        "endpoints": {
            "tra_tu":        "GET /api/v1/words/lookup?q=cat",
            "danh_sach":     "GET /api/v1/words",
            "theo_chu_de":   "GET /api/v1/words?topic=animals",
            "theo_trinh_do": "GET /api/v1/words?level=A1",
            "tim_kiem":      "GET /api/v1/words?search=mèo",
            "ngau_nhien":    "GET /api/v1/words/random?count=5",
            "chu_de":        "GET /api/v1/words/topics",
            "trinh_do":      "GET /api/v1/words/levels",
            "them_tu":       "POST /api/v1/words",
            "cap_nhat":      "PUT /api/v1/words/{id}",
            "xoa_tu":        "DELETE /api/v1/words/{id}",
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)