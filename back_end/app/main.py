# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.database import get_db
from app import schemas, crud, models, security, auth

app = FastAPI(title="TienQuan Bike API")

# Tích hợp Router xác thực & đăng ký tài khoản
app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"message": "Chào mừng bạn đến với Grab Clone / TienQuanBike API!"}

# --- CUSTOMER ENDPOINTS ---
@app.post("/customers/", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED, tags=["Khách hàng (Customer)"])
def create_customer(customer: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.phone == customer.phone).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Số điện thoại này đã được đăng ký.")
    return crud.create_customer(db, customer)

@app.get("/customers/{c_id}", response_model=schemas.UserOut, tags=["Khách hàng (Customer)"])
def read_customer(c_id: UUID, db: Session = Depends(get_db)):
    db_customer = crud.get_customer(db, c_id)
    if not db_customer:
        raise HTTPException(status_code=404, detail="Không tìm thấy khách hàng.")
    return db_customer


# --- DRIVER ENDPOINTS ---
@app.post("/drivers/", response_model=schemas.DriverOut, status_code=status.HTTP_201_CREATED, tags=["Tài xế (Driver)"])
def create_driver(driver: schemas.DriverCreate, db: Session = Depends(get_db)):
    existing_license = db.query(models.Driver).filter(models.Driver.driving_license_no == driver.driving_license_no).first()
    if existing_license:
        raise HTTPException(status_code=400, detail="Biển số/Số bằng lái xe đã tồn tại.")
    
    return crud.create_driver(db, driver)

@app.get("/drivers/{d_id}", response_model=schemas.DriverOut, tags=["Tài xế (Driver)"])
def read_driver(d_id: UUID, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, d_id)
    if not db_user or not db_user.driver_profile:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ tài xế.")

    return db_user


# --- TRIP ENDPOINTS ---
@app.post("/trips/", response_model=schemas.TripOut, status_code=status.HTTP_201_CREATED, tags=["Chuyến đi (Trip)"])
def create_trip(
    trip: schemas.TripCreate,
    db: Session = Depends(get_db),
    current_customer: models.User = Depends(security.get_current_customer)
):
    """
    Tạo yêu cầu chuyến đi (Chỉ Khách hàng đã đăng nhập mới được thực hiện).
    """
    # Gán hoặc kiểm tra p_id trùng với ID người dùng đang đăng nhập
    if trip.p_id != current_customer.id:
        trip.p_id = current_customer.id

    return crud.create_trip(db, trip)

@app.get("/trips/{trip_id}", response_model=schemas.TripOut, tags=["Chuyến đi (Trip)"])
def read_trip(
    trip_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    db_trip = crud.get_trip(db, trip_id)
    if not db_trip:
        raise HTTPException(status_code=404, detail="Không tìm thấy chuyến đi.")
    return db_trip

@app.put("/trips/{trip_id}/status", response_model=schemas.TripOut, tags=["Chuyến đi (Trip)"])
def update_trip(
    trip_id: UUID,
    trip_update: schemas.TripUpdateStatus,
    db: Session = Depends(get_db),
    current_driver: models.Driver = Depends(security.get_current_driver)
):
    """
    Cập nhật trạng thái chuyến đi (Chỉ Tài xế đã đăng nhập mới được thực hiện).
    """
    # Tự động gắn ID của tài xế đang đăng nhập nếu chưa có
    if not trip_update.d_id:
        trip_update.d_id = current_driver.user_id

    db_trip = crud.update_trip_status(db, trip_id, trip_update)
    if not db_trip:
        raise HTTPException(status_code=404, detail="Không tìm thấy chuyến đi để cập nhật.")
    return db_trip