from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from app.models import User, Customer, Driver, Trip
from app import schemas

# --- USER CRUD ---
def get_user(db: Session, user_id: UUID):
    return db.query(User).filter(User.id == user_id).first()

# --- CUSTOMER CRUD ---
def get_customer(db: Session, c_id: UUID):
    return db.query(Customer).filter(Customer.c_id == c_id).first()

def create_customer(db: Session, customer_in: schemas.CustomerCreate):
    db_customer = Customer(
        name=customer_in.name,
        phone=customer_in.phone,
        password=customer_in.password,
        rating=customer_in.rating,
        total_rides=customer_in.total_rides
    )
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

# --- DRIVER CRUD ---
def get_driver(db: Session, d_id: UUID):
    return db.query(Driver).filter(Driver.d_id == d_id).first()

def create_driver(db: Session, driver_in: schemas.DriverCreate):
    db_driver = Driver(
        name=driver_in.name,
        phone=driver_in.phone,
        password=driver_in.password,
        driving_license_no=driver_in.driving_license_no,
        identity_card_no=driver_in.identity_card_no,
        wallet_balance=driver_in.wallet_balance,
        rating=driver_in.rating,
        is_online=driver_in.is_online,
        status=driver_in.status
    )
    db.add(db_driver)
    db.commit()
    db.refresh(db_driver)
    return db_driver

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
