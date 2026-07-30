from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from app.models import User, Driver, Trip
from app import schemas

# --- USER CRUD ---
def get_user(db: Session, user_id: UUID):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_identifier(db: Session, identifier: str):
    return db.query(User).filter(
        (User.phone == identifier) | (User.email == identifier)
    ).first()

def get_user_roles(db: Session, user_id: UUID):
    roles = ["customer"]  # Mọi user mặc định đều có quyền customer
    driver_profile = db.query(Driver).filter(Driver.user_id == user_id).first()
    if driver_profile:
        roles.append("driver")
    return roles

def authenticate_user(db: Session, identifier: str, password: str, login_as: str = "customer"):
    user = get_user_by_identifier(db, identifier)
    if not user:
        return None
    # So sánh trực tiếp mật khẩu dạng plain-text
    if user.password != password:
        return None

    roles = get_user_roles(db, user.id)

    # Nếu chọn đăng nhập bằng tài xế nhưng chưa đăng ký tài xế
    if login_as == "driver" and "driver" not in roles:
        return None, "NOT_A_DRIVER"

    active_role = login_as if login_as in roles else "customer"
    return user, roles, active_role


# --- CUSTOMER CRUD ---
def get_customer(db: Session, c_id: UUID):
    return get_user(db, user_id=c_id)

def create_customer(db: Session, customer_in: schemas.UserCreate):
    rating_val = getattr(customer_in, 'rating', None)
    total_rides_val = getattr(customer_in, 'total_rides', None)
    
    db_user = User(
        name=customer_in.name,
        phone=customer_in.phone,
        email=customer_in.email,
        password=customer_in.password,
        rating=rating_val if rating_val is not None else 5.0,
        total_rides=total_rides_val if total_rides_val is not None else 0
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# --- DRIVER CRUD ---
def get_driver(db: Session, user_id: UUID):
    return db.query(Driver).filter(Driver.user_id == user_id).first()

def create_driver(db: Session, driver_in: schemas.DriverCreate):
    # Tạo User mới
    new_user = User(
        name=driver_in.name,
        phone=driver_in.phone,
        email=driver_in.email,
        password=driver_in.password,
        rating=5.0,
        total_rides=0
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Đã có User -> Bổ sung Driver Profile vào bảng driver
    db_driver = Driver(
        user_id=new_user.id,
        driving_license_no=driver_in.driving_license_no,
        identity_card_no=driver_in.identity_card_no,
        wallet_balance=driver_in.wallet_balance if driver_in.wallet_balance is not None else 0.0,
        rating=driver_in.rating if driver_in.rating is not None else 5.0,
        is_online=driver_in.is_online if driver_in.is_online is not None else False,
        status=driver_in.status if driver_in.status is not None else "offline"
    )
    db.add(db_driver)
    db.commit()
    db.refresh(db_driver)
    db.refresh(new_user)
    return new_user

def create_driver_profile_for_existing_user(db: Session, user_id: UUID, upgrade_in: schemas.DriverUpgrade):
    db_driver = Driver(
        user_id=user_id,
        driving_license_no=upgrade_in.driving_license_no,
        identity_card_no=upgrade_in.identity_card_no,
        wallet_balance=upgrade_in.wallet_balance if upgrade_in.wallet_balance is not None else 0.0,
        rating=upgrade_in.rating if upgrade_in.rating is not None else 5.0,
        is_online=upgrade_in.is_online if upgrade_in.is_online is not None else False,
        status=upgrade_in.status if upgrade_in.status is not None else "offline"
    )
    db.add(db_driver)
    db.commit()
    db.refresh(db_driver)
    user = get_user(db, user_id)
    return user



# --- TRIP CRUD ---
def get_trip(db: Session, trip_id: UUID):
    return db.query(Trip).filter(Trip.trip_id == trip_id).first()

def create_trip(db: Session, trip_in: schemas.TripCreate):
    db_trip = Trip(
        p_id=trip_in.p_id,
        start_lat=trip_in.start_lat,
        start_lng=trip_in.start_lng,
        start_address=trip_in.start_address,
        dest_lat=trip_in.dest_lat,
        dest_lng=trip_in.dest_lng,
        dest_address=trip_in.dest_address,
        fee=trip_in.fee,
        status="requested"
    )
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)
    return db_trip

def update_trip_status(db: Session, trip_id: UUID, trip_update: schemas.TripUpdateStatus):
    db_trip = get_trip(db, trip_id)
    if not db_trip:
        return None
    
    db_trip.status = trip_update.status
    
    if trip_update.d_id:
        db_trip.d_id = trip_update.d_id
        
    if trip_update.status == "accepted":
        db_trip.accepted_at = datetime.utcnow()
    elif trip_update.status == "completed":
        db_trip.completed_at = datetime.utcnow()
        
    db.commit()
    db.refresh(db_trip)
    return db_trip
