from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.routers.auth_router import router as auth_router
from app.routers.content_router import router as content_router  # <-- thêm dòng này

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"detail": "Lỗi server, vui lòng thử lại sau."},
    )

app.include_router(auth_router, prefix="/api/v1")
app.include_router(content_router, prefix="/api/v1")   # <-- thêm dòng này

@app.get("/health", tags=["System"])
async def health_check() -> dict:
    return {"status": "ok", "app": settings.APP_NAME}