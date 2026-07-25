from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal

# --- USER SCHEMAS ---
import re
from pydantic import BaseModel, Field, field_validator
class UserBase(BaseModel):
    name: str = Field(..., max_length=50, description="Tên người dùng")
    phone: str = Field(..., min_length=10, max_length=10, description="Số điện thoại")
    email: str = Field(..., max_length=100, description="Địa chỉ Email")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        # Xóa khoảng trắng thừa
        v = v.strip()
        # Sử dụng biểu thức chính quy (Regex) để kiểm tra:
        # Bắt đầu bằng số 0 và theo sau là 9 chữ số khác (Tổng cộng 10 số)
        phone_regex = r"^0\d{9}$"
        if not re.match(phone_regex, v):
            raise ValueError("Số điện thoại không hợp lệ.")
        return v

    @field_validator("email")
    @classmethod
    def validate_gmail(cls, v: str) -> str:
        # Chuẩn hóa chuỗi: xóa khoảng trắng và chuyển về chữ thường
        v = v.strip().lower()
        
        if not v.endswith("@gmail.com"):
            raise ValueError("Hệ thống chỉ hỗ trợ email có đuôi @gmail.com.")
        return v

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: UUID
    class Config:
        from_attributes = True


# --- CUSTOMER SCHEMAS ---
class CustomerCreate(UserCreate):
    rating: Optional[Decimal] = 5.0
    total_rides: Optional[int] = 0

class CustomerOut(UserOut):
    rating: Decimal
    total_rides: int
    class Config:
        from_attributes = True


# --- DRIVER SCHEMAS ---
class DriverCreate(UserCreate):
    driving_license_no: str = Field(..., max_length=50)
    identity_card_no: str = Field(..., max_length=20)
    wallet_balance: Optional[Decimal] = 0.0
    rating: Optional[Decimal] = 5.0
    is_online: Optional[bool] = False
    status: Optional[str] = "offline"

class DriverOut(UserOut):
    driving_license_no: str
    identity_card_no: str
    wallet_balance: Decimal
    rating: Decimal
    is_online: bool
    status: str
    class Config:
        from_attributes = True


# --- TRIP SCHEMAS ---
class TripCreate(BaseModel):
    p_id: UUID
    start_lat: Decimal
    start_lng: Decimal
    start_address: str = Field(..., max_length=255)
    dest_lat: Decimal
    dest_lng: Decimal
    dest_address: str = Field(..., max_length=255)
    fee: Decimal

class TripUpdateStatus(BaseModel):
    status: str  # accepted, picked_up, completed, cancelled
    d_id: Optional[UUID] = None  # Gửi lên d_id khi tài xế nhận chuyến

class TripOut(BaseModel):
    trip_id: UUID
    p_id: UUID
    d_id: Optional[UUID] = None
    start_lat: Decimal
    start_lng: Decimal
    start_address: str
    dest_lat: Decimal
    dest_lng: Decimal
    dest_address: str
    fee: Decimal
    status: str
    requested_at: datetime
    accepted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
