# 📚 LexiRise API - Backend

Một ứng dụng backend học tiếng Anh được xây dựng bằng **FastAPI** và **MySQL**.

---

## 📋 Mục Lục

1. [Yêu Cầu Hệ Thống](#yêu-cầu-hệ-thống)
2. [Cài Đặt Nhanh](#cài-đặt-nhanh)
3. [Cấu Hình Chi Tiết](#cấu-hình-chi-tiết)
4. [Thiết Lập Cơ Sở Dữ Liệu](#thiết-lập-cơ-sở-dữ-liệu)
5. [Chạy Ứng Dụng](#chạy-ứng-dụng)
6. [Chạy Tests](#chạy-tests)
7. [Troubleshooting](#troubleshooting)

---

## 🔧 Yêu Cầu Hệ Thống

Trước khi bắt đầu, đảm bảo máy của bạn đã cài đặt:

- **Python 3.8+** - [Tải Python](https://www.python.org/downloads/)
- **MySQL 5.7+** - [Tải MySQL](https://www.mysql.com/downloads/)
- **Git** (để clone repo) - [Tải Git](https://git-scm.com/)
- **pip** (đi kèm với Python)

### Kiểm Tra Phiên Bản
```bash
python --version        # Nên là Python 3.8+
mysql --version        # Nên là MySQL 5.7+
pip --version
```

---

## 🚀 Cài Đặt Nhanh

### Bước 1: Clone Repository

```bash
git clone https://github.com/your-username/my-python-backend.git
cd my-python-backend
```

### Bước 2: Tạo Virtual Environment

**Trên Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Trên macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Bước 3: Cài Đặt Dependencies

```bash
pip install -r requirements.txt
```

### Bước 4: Cấu Hình Environment Variables

```bash
cp .env.example .env
```

Sau đó chỉnh sửa file `.env` với các giá trị phù hợp (xem phần **Cấu Hình Chi Tiết** dưới đây).

### Bước 5: Thiết Lập Database

```bash
python test_db.py    # Kiểm tra kết nối database
```

### Bước 6: Chạy Ứng Dụng

```bash
python -m uvicorn app.main:app --reload
```

Truy cập: `http://localhost:8000/docs` để xem API documentation.

---

## 🔐 Cấu Hình Chi Tiết

### File `.env` - Biến Môi Trường

Sau khi chạy `cp .env.example .env`, hãy chỉnh sửa file `.env` với các thông tin của bạn:

#### 1️⃣ Cấu Hình Ứng Dụng
```env
# App
APP_NAME=LexiRise API          # Tên ứng dụng
DEBUG=false                     # true = chế độ debug, false = production
```

**Hướng dẫn:**
- `DEBUG`: Để `false` khi deploy production để tăng bảo mật. Để `true` khi phát triển để xem chi tiết lỗi.

#### 2️⃣ Cấu Hình Database MySQL
```env
# Database
DB_HOST=localhost              # Địa chỉ MySQL server (localhost nếu cài local)
DB_PORT=3306                   # Cổng MySQL (mặc định 3306)
DB_USER=root                   # Username MySQL
DB_PASSWORD=1234               # Password MySQL
DB_NAME=lexirise               # Tên database
```

**Hướng dẫn:**
- **Để sử dụng MySQL cục bộ:**
  - Nếu dùng XAMPP: `DB_HOST=localhost`, `DB_USER=root`, `DB_PASSWORD=` (để trống)
  - Nếu dùng MySQL riêng: điền username/password bạn đã tạo
  
- **Để kết nối MySQL trên server khác:**
  - `DB_HOST=192.168.1.100` (IP server)
  - `DB_USER=remote_user`
  - `DB_PASSWORD=your_password`

- **Tạo Database:**
  ```bash
  # Đăng nhập MySQL
  mysql -u root -p
  
  # Trong MySQL shell
  CREATE DATABASE lexirise;
  EXIT;
  ```

#### 3️⃣ Cấu Hình JWT (Bảo Mật Token)
```env
# JWT
JWT_SECRET_KEY=59fd59b2986e13ba42ea01ee959643db77922bdd50f67d774ee1ac451e4c55be
JWT_ALGORITHM=HS256            # Thuật toán mã hóa (giữ nguyên)
ACCESS_TOKEN_EXPIRE_MINUTES=1440     # Thời gian hết hạn token (phút) - 1440 = 1 ngày
REFRESH_TOKEN_EXPIRE_DAYS=30          # Thời gian hết hạn refresh token (ngày)
```

**Hướng dẫn:**
- **`JWT_SECRET_KEY`**: Khóa bí mật để mã hóa token. **⚠️ QUAN TRỌNG: Thay đổi giá trị này trong production!**
  
  Tạo khóa mới (bất kỳ chuỗi hex 64 ký tự):
  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```

- **`ACCESS_TOKEN_EXPIRE_MINUTES`**: Bao lâu token hết hạn
  - 60 = 1 giờ
  - 1440 = 1 ngày (khuyến nghị)
  - 5 = 5 phút (để test)

#### 4️⃣ Cấu Hình Email SMTP (Gửi Email)
```env
# Email SMTP
SMTP_HOST=smtp.gmail.com       # Server SMTP
SMTP_PORT=587                  # Cổng SMTP
SMTP_USER=your-email@gmail.com # Email để gửi
SMTP_PASSWORD=app-password     # Mật khẩu ứng dụng
EMAIL_FROM=your-email@gmail.com # Email hiển thị gửi từ
```

**Hướng dẫn cho Gmail:**
1. Bật 2-step verification: https://myaccount.google.com/security
2. Tạo App Password: https://myaccount.google.com/apppasswords
3. Sao chép password 16 ký tự vào `SMTP_PASSWORD`
4. Điền email vào `SMTP_USER` và `EMAIL_FROM`

**Hướng dẫn cho Outlook:**
```env
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USER=your-email@outlook.com
SMTP_PASSWORD=your-password
```

#### 5️⃣ Cấu Hình URL Frontend (Cho Reset Password)
```env
# Frontend URL
RESET_PASSWORD_URL=http://localhost:3000/reset-password
```

**Hướng dẫn:**
- **Development**: `http://localhost:3000/reset-password`
- **Production**: `https://yourdomain.com/reset-password`

---

## 💾 Thiết Lập Cơ Sở Dữ Liệu

### 1. Tạo Database

```bash
# Đăng nhập MySQL
mysql -u root -p

# Trong MySQL shell
CREATE DATABASE lexirise CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### 2. Kiểm Tra Kết Nối

```bash
python test_db.py
```

Nếu kết nối thành công, bạn sẽ thấy:
```
✓ Database connection successful
```

Nếu có lỗi, kiểm tra:
- MySQL server đang chạy?
- Username/password trong `.env` đúng không?
- Database `lexirise` đã được tạo chưa?

### 3. Khởi Tạo Bảng (Tùy Chọn)

Nếu có file migration hoặc SQL script:
```bash
mysql -u root -p lexirise < english_app.sql
```

---

## ▶️ Chạy Ứng Dụng

### Chế Độ Development (Với Auto-Reload)

```bash
python -m uvicorn app.main:app --reload
```

**Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

- **API docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc

### Chế Độ Production

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Tùy chọn:
- `--host 0.0.0.0`: Cho phép truy cập từ bên ngoài
- `--port 8000`: Thay đổi port
- `--workers 4`: Số worker processes

---

## 🧪 Chạy Tests

### Chạy Tất Cả Tests

```bash
pytest
```

### Chạy Với Coverage Report

```bash
pytest --cov=app
```

### Chạy Test File Cụ Thể

```bash
pytest tests/test_auth.py
```

### Chạy Với Output Chi Tiết

```bash
pytest -v
```

---

## 📊 Cấu Trúc Thư Mục

```
my-python-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── core/
│   │   ├── config.py        # Cấu hình app
│   │   ├── database.py      # Kết nối database
│   │   ├── security.py      # JWT, password hashing
│   │   └── dependencies.py  # Dependency injection
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas (validation)
│   ├── routers/             # API endpoints
│   └── services/            # Business logic
├── tests/                   # Unit tests
├── .env.example            # Template file .env
├── .env                    # ⚠️ KHÔNG PUSH LÊN GIT
├── requirements.txt        # Python dependencies
└── README.md              # File này
```

---

## 🔍 Troubleshooting

### Lỗi: ModuleNotFoundError

**Lỗi:**
```
ModuleNotFoundError: No module named 'app'
```

**Giải pháp:**
- Đảm bảo virtual environment đã được kích hoạt
- Cài lại dependencies: `pip install -r requirements.txt`

### Lỗi: MySQL Connection Error

**Lỗi:**
```
pymysql.err.OperationalError: (2003, "Can't connect to MySQL server")
```

**Giải pháp:**
- Kiểm tra MySQL server đang chạy: `mysql -u root -p`
- Kiểm tra `DB_HOST`, `DB_USER`, `DB_PASSWORD` trong `.env`
- Tạo database: `CREATE DATABASE lexirise;`

### Lỗi: Port 8000 Đã Được Sử Dụng

**Lỗi:**
```
error: Address already in use
```

**Giải pháp:**
- Dùng port khác: `uvicorn app.main:app --port 8001`
- Hoặc tắt process đang dùng port 8000

### Lỗi: SMTP Email Không Gửi

**Kiểm tra:**
- Gmail: Đã bật 2-step verification?
- Đã tạo App Password?
- SMTP_USER và SMTP_PASSWORD đúng?

Kiểm tra log:
```bash
python test_pass.py
```

---

## 📝 Các Lệnh Hữu Ích

```bash
# Cài thêm package
pip install package-name

# Cập nhật requirements
pip freeze > requirements.txt

# Kiểm tra syntax
python -m py_compile app/main.py

# Format code (nếu có black)
black app/

# Lint code (nếu có pylint)
pylint app/

# Xem biến môi trường hiện tại
python -c "from app.core.config import settings; print(settings)"

# Tạo khóa JWT mới
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🤝 Support & Contact

Nếu gặp vấn đề:
1. Kiểm tra lại cấu hình `.env`
2. Xem logs chi tiết: Chạy app với `--reload` để xem lỗi
3. Tạo issue trên GitHub hoặc liên hệ team

---

## 📄 Cấp Phép

MIT License
