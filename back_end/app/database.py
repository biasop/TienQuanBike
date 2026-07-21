# app/database.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Đọc file .env ở thư mục gốc
from pathlib import Path
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

import urllib.parse

# Tạo chuỗi kết nối PostgreSQL
# Mã hóa mật khẩu đề phòng trường hợp chứa ký tự đặc biệt như @
encoded_password = urllib.parse.quote_plus(DB_PASSWORD or "")
DATABASE_URL = f"postgresql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Tạo Engine kết nối
engine = create_engine(DATABASE_URL)

# Tạo Session để thao tác với DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class để các model kế thừa
Base = declarative_base()

# Hàm tiện ích để lấy session database cho mỗi request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()