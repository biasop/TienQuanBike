# main.py
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db

app = FastAPI(title="Grab Clone API")

@app.get("/")
def read_root():
    return {"message": "Chào mừng bạn đến với Grab Clone API!"}

# API chạy thử để kiểm tra kết nối Database có thực sự hoạt động
@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    try:
        # Thực thi một câu lệnh SQL đơn giản để kiểm tra kết nối
        db.execute(text("SELECT 1"))
        return {"status": "Thành công", "message": "Kết nối Database PostgreSQL cục bộ hoạt động tốt!"}
    except Exception as e:
        return {"status": "Thất bại", "error": str(e)}