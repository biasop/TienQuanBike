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
pip install fastapi uvicorn sqlalchemy psycopg2 pydantic[email] python-dotenv
```

### 2. Cấu hình biến môi trường
Tạo file `.env` ở thư mục gốc của dự án (hoặc kiểm tra file `.env` đã có sẵn) và cấu hình các thông số kết nối Database:
```env
DB_USER=tên_đăng_nhập_postgres
DB_PASSWORD=mật_khẩu_postgres
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=TienQuan
```

---

## 🚀 Hướng dẫn khởi chạy API Server

Có 2 cách để khởi chạy dự án tùy thuộc vào vị trí của bạn trong Terminal:

### Cách 1: Chạy từ thư mục gốc dự án (`TienQuanBike/`)
Nếu terminal của bạn đang mở ở thư mục cha, chạy lệnh:
```bash
python -m uvicorn back_end.app.main:app --reload
```

### Cách 2: Chạy từ thư mục `back_end/`
Nếu terminal đang đứng ở thư mục `back_end/`, trước tiên di chuyển vào (nếu chưa) rồi chạy:
```bash
cd back_end
uvicorn app.main:app --reload
```

---

## 🔍 Kiểm tra và Chạy thử API (Swagger UI)

Khi server khởi chạy thành công, truy cập đường dẫn sau trên trình duyệt để sử dụng giao diện kiểm thử API tự động:
👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

### Các chức năng API mẫu đã hỗ trợ:
1. **Khách hàng (Customer):**
   * `POST /customers/`: Đăng ký tài khoản khách hàng mới (hệ thống tự tạo tài khoản User cơ bản và liên kết tự động tới bảng Customer).
   * `GET /customers/{c_id}`: Tra cứu thông tin khách hàng bằng mã ID.
2. **Tài xế (Driver):**
   * `POST /drivers/`: Đăng ký tài xế mới (yêu cầu điền đầy đủ biển số xe, căn cước công dân).
   * `GET /drivers/{d_id}`: Tra cứu thông tin tài xế.
3. **Chuyến đi (Trip):**
   * `POST /trips/`: Khách hàng tạo yêu cầu đặt chuyến đi (chứa thông tin điểm đón, điểm trả, khoảng cách và cước phí).
   * `GET /trips/{trip_id}`: Kiểm tra trạng thái chuyến đi.
   * `PUT /trips/{trip_id}/status`: Cập nhật trạng thái chuyến đi (Tài xế nhận chuyến `accepted`, tài xế đã đón khách `picked_up`, hoàn thành chuyến `completed`, hủy chuyến `cancelled`).
