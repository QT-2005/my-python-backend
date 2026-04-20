from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings


engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,    
    pool_recycle=3600,     
    pool_size=10,
    max_overflow=20,
    echo=settings.DEBUG,   
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


# Dependency dùng trong router
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    from app.models import word  
    Base.metadata.create_all(bind=engine)
    print("✅ Tạo bảng thành công!")


def check_connection():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"✅ Kết nối MySQL thành công: {settings.MYSQL_HOST}/{settings.MYSQL_DB}")
        return True
    except Exception as e:
        print(f"❌ Kết nối MySQL thất bại: {e}")
        print("   → Kiểm tra lại MYSQL_PASSWORD trong file .env")
        return False