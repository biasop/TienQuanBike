import uuid
from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False)
    phone = Column(String(15), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=False)

    # Thuộc tính mặc định của Khách hàng
    rating = Column(Numeric(3, 2), default=5.0)
    total_rides = Column(Integer, default=0)

    # Relationship tới Hồ sơ tài xế (Driver Profile 1-to-1)
    driver_profile = relationship("Driver", back_populates="user", uselist=False)

    # Relationships tới các Chuyến đi (Trip)
    customer_trips = relationship("Trip", foreign_keys="[Trip.p_id]", back_populates="customer")
    driver_trips = relationship("Trip", foreign_keys="[Trip.d_id]", back_populates="driver")


class Driver(Base):
    __tablename__ = "driver"

    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), primary_key=True)
    driving_license_no = Column(String(50), unique=True, nullable=False)
    identity_card_no = Column(String(20), unique=True, nullable=False)
    wallet_balance = Column(Numeric(15, 2), default=0.0)
    rating = Column(Numeric(3, 2), default=5.0)
    is_online = Column(Boolean, default=False)
    status = Column(String(20), default="offline")

    user = relationship("User", back_populates="driver_profile")


class Trip(Base):
    __tablename__ = "trip"

    trip_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    p_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    d_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)

    start_lat = Column(Numeric(10, 8), nullable=False)
    start_lng = Column(Numeric(10, 8), nullable=False)
    start_address = Column(String(255), nullable=False)
    
    dest_lat = Column(Numeric(10, 8), nullable=False)
    dest_lng = Column(Numeric(10, 8), nullable=False)
    dest_address = Column(String(255), nullable=False)
    
    fee = Column(Numeric(15, 2), nullable=False)
    status = Column(String(20), default="requested") # requested, accepted, picked_up, completed, cancelled

    requested_at = Column(DateTime, server_default=func.now())
    accepted_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    customer = relationship("User", foreign_keys=[p_id], back_populates="customer_trips")
    driver = relationship("User", foreign_keys=[d_id], back_populates="driver_trips")
