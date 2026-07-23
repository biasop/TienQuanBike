# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.database import get_db
from app import schemas, crud

app = FastAPI(title="TienQuan Bike API")

@app.get("/")
def read_root():
    return {"message": "Chào mừng bạn đến với Grab Clone / TienQuanBike API!"}

# --- CUSTOMER ENDPOINTS ---
@app.post("/customers/", response_model=schemas.CustomerOut, status_code=status.HTTP_201_CREATED)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    # Kiểm tra xem phone đã tồn tại trong bảng User chưa
    from app.models import User
    existing_user = db.query(User).filter(User.phone == customer.phone).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Số điện thoại này đã được đăng ký.")
    return crud.create_customer(db, customer)

@app.get("/customers/{c_id}", response_model=schemas.CustomerOut)
def read_customer(c_id: UUID, db: Session = Depends(get_db)):
    db_customer = crud.get_customer(db, c_id)
    if not db_customer:
        raise HTTPException(status_code=404, detail="Không tìm thấy khách hàng.")
    return db_customer


# --- DRIVER ENDPOINTS ---
@app.post("/drivers/", response_model=schemas.DriverOut, status_code=status.HTTP_201_CREATED)
def create_driver(driver: schemas.DriverCreate, db: Session = Depends(get_db)):
    from app.models import User, Driver
    # Kiểm tra phone
    existing_user = db.query(User).filter(User.phone == driver.phone).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Số điện thoại này đã được đăng ký.")
    # Kiểm tra biển số xe
    existing_license = db.query(Driver).filter(Driver.driving_license_no == driver.driving_license_no).first()
    if existing_license:
        raise HTTPException(status_code=400, detail="Biển số xe đã tồn tại.")
    return crud.create_driver(db, driver)

@app.get("/drivers/{d_id}", response_model=schemas.DriverOut)
def read_driver(d_id: UUID, db: Session = Depends(get_db)):
    db_driver = crud.get_driver(db, d_id)
    if not db_driver:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài xế.")
    return db_driver


# --- TRIP ENDPOINTS ---
@app.post("/trips/", response_model=schemas.TripOut, status_code=status.HTTP_201_CREATED)
def create_trip(trip: schemas.TripCreate, db: Session = Depends(get_db)):
    # Đảm bảo Customer tồn tại
    db_customer = crud.get_customer(db, trip.p_id)
    if not db_customer:
        raise HTTPException(status_code=404, detail="Khách hàng không tồn tại.")
    return crud.create_trip(db, trip)

@app.get("/trips/{trip_id}", response_model=schemas.TripOut)
def read_trip(trip_id: UUID, db: Session = Depends(get_db)):
    db_trip = crud.get_trip(db, trip_id)
    if not db_trip:
        raise HTTPException(status_code=404, detail="Không tìm thấy chuyến đi.")
    return db_trip

@app.put("/trips/{trip_id}/status", response_model=schemas.TripOut)
def update_trip(trip_id: UUID, trip_update: schemas.TripUpdateStatus, db: Session = Depends(get_db)):
    if trip_update.d_id:
        db_driver = crud.get_driver(db, trip_update.d_id)
        if not db_driver:
            raise HTTPException(status_code=404, detail="Tài xế không tồn tại.")
            
    db_trip = crud.update_trip_status(db, trip_id, trip_update)
    if not db_trip:
        raise HTTPException(status_code=404, detail="Không tìm thấy chuyến đi để cập nhật.")
    return db_trip