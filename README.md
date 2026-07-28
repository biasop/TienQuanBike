# Grab Clone - TienQuanBike API Backend

Dự án phát triển API Backend cho ứng dụng đặt xe máy (TienQuanBike) sử dụng **FastAPI** và **PostgreSQL** kết hợp với **SQLAlchemy ORM**.

---

## 🛠️ Yêu cầu hệ thống
* Python 3.8 trở lên
* Cơ sở dữ liệu PostgreSQL (cục bộ hoặc server đám mây)

---

## ⚙️ Hướng dẫn cài đặt

### 1. Cài đặt thư viện
Chạy lệnh sau trong Terminal để cài đặt toàn bộ các gói thư viện cần thiết:
```bash
pip install fastapi uvicorn sqlalchemy psycopg2 pydantic[email] python-dotenv pyjwt python-multipart
```

### 2. Cấu hình biến môi trường
Tạo file `.env` ở thư mục gốc của dự án (hoặc kiểm tra file `.env` đã có sẵn) và cấu hình các thông số:
```env
DB_USER=postgres
DB_PASSWORD=mật_khẩu_postgres
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=TienQuan

SECRET_KEY=tienquanbike_secret_key_super_secret_12345
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

---

## 🚀 Hướng dẫn khởi chạy API Server

Có 2 cách để khởi chạy dự án tùy thuộc vào vị trí của bạn trong Terminal:

### Cách 1: Chạy từ thư mục gốc dự án (`TienQuanBike/`)
```bash
python -m uvicorn back_end.app.main:app --reload
```

### Cách 2: Chạy từ thư mục `back_end/`
```bash
cd back_end
uvicorn app.main:app --reload
```

---

## 🔍 Kiểm tra và Chạy thử API (Swagger UI)

Khi server khởi chạy thành công, truy cập đường dẫn sau trên trình duyệt để sử dụng giao diện kiểm thử API tự động:
👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

---

## 🔑 Các chức năng API Đăng ký, Đăng nhập & Phân quyền (Auth):

1. **Xác thực & Tài khoản (`/auth`):**
   * `POST /auth/register/customer`: Đăng ký tài khoản Khách hàng mới.
   * `POST /auth/register/driver`: Đăng ký tài khoản Tài xế mới (yêu cầu Bằng lái xe, CCCD).
   * `POST /auth/login`: Đăng nhập lấy JWT Access Token (hỗ trợ nút **Authorize 🔒** trên Swagger UI). Nhập SĐT hoặc Email vào ô `username`.
   * `POST /auth/login-json`: Đăng nhập lấy Token bằng JSON Body `{ "identifier": "SĐT/Email", "password": "..." }` (phù hợp cho Web Frontend / App Mobile).
   * `GET /auth/me`: Trả về thông tin cá nhân và vai trò của người dùng hiện tại đang đăng nhập.

2. **Chuyến đi & Phân quyền (`/trips`):**
   * `POST /trips/`: Khách hàng tạo yêu cầu đặt chuyến đi (**Yêu cầu Token vai trò Customer**).
   * `GET /trips/{trip_id}`: Kiểm tra chi tiết chuyến đi (**Yêu cầu Token đã đăng nhập**).
   * `PUT /trips/{trip_id}/status`: Tài xế nhận chuyến hoặc cập nhật trạng thái chuyến đi (**Yêu cầu Token vai trò Driver**).

