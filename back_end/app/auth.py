from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app import schemas, crud, models, security

router = APIRouter(prefix="/auth", tags=["Xác thực & Tài khoản (Auth)"])

# --- ĐĂNG KÝ KHÁCH HÀNG / NGƯỜI DÙNG CHUNG ---
@router.post("/register/customer", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register_customer(customer: schemas.UserCreate, db: Session = Depends(get_db)):
    # Kiểm tra SĐT đã đăng ký chưa
    existing_phone = db.query(models.User).filter(models.User.phone == customer.phone).first()
    if existing_phone:
        raise HTTPException(status_code=400, detail="Số điện thoại này đã được sử dụng.")
    
    # Kiểm tra Email đã đăng ký chưa
    existing_email = db.query(models.User).filter(models.User.email == customer.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email này đã được sử dụng.")

    return crud.create_customer(db, customer)


# --- ĐĂNG KÝ HỒ SƠ TÀI XẾ MỚI (CHƯA CÓ TÀI KHOẢN) ---
@router.post("/register/driver", response_model=schemas.DriverOut, status_code=status.HTTP_201_CREATED)
def register_driver(driver: schemas.DriverCreate, db: Session = Depends(get_db)):
    # Kiểm tra Bằng lái xe
    existing_license = db.query(models.Driver).filter(models.Driver.driving_license_no == driver.driving_license_no).first()
    if existing_license:
        raise HTTPException(status_code=400, detail="Số bằng lái xe đã tồn tại trên hệ thống.")

    # Kiểm tra CCCD
    existing_id_card = db.query(models.Driver).filter(models.Driver.identity_card_no == driver.identity_card_no).first()
    if existing_id_card:
        raise HTTPException(status_code=400, detail="Số căn cước công dân đã tồn tại trên hệ thống.")

    # Kiểm tra SĐT đã tồn tại chưa
    existing_phone = db.query(models.User).filter(models.User.phone == driver.phone).first()
    if existing_phone:
        raise HTTPException(
            status_code=400,
            detail="Số điện thoại này đã được sử dụng. Vui lòng Đăng nhập tài khoản và chọn Nâng cấp làm Tài xế."
        )

    # Kiểm tra Email đã tồn tại chưa
    existing_email = db.query(models.User).filter(models.User.email == driver.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email này đã được sử dụng.")

    return crud.create_driver(db, driver)


# --- NÂNG CẤP TÀI KHOẢN TÀI XẾ (DÀNH CHO TÀI KHOẢN ĐÃ ĐĂNG NHẬP) ---
@router.post("/upgrade/driver", response_model=schemas.DriverOut, status_code=status.HTTP_201_CREATED)
def upgrade_to_driver(
    upgrade_data: schemas.DriverUpgrade,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Nâng cấp tài khoản đang đăng nhập hiện tại lên làm Tài xế (Chỉ cần gửi Bằng lái & CCCD).
    """
    # Kiểm tra xem tài khoản này đã có profile tài xế chưa
    existing_driver = crud.get_driver(db, current_user.id)
    if existing_driver:
        raise HTTPException(status_code=400, detail="Tài khoản này đã đăng ký hồ sơ Tài xế trước đó.")

    # Kiểm tra Bằng lái xe trùng
    existing_license = db.query(models.Driver).filter(models.Driver.driving_license_no == upgrade_data.driving_license_no).first()
    if existing_license:
        raise HTTPException(status_code=400, detail="Số bằng lái xe đã tồn tại trên hệ thống.")

    # Kiểm tra CCCD trùng
    existing_id_card = db.query(models.Driver).filter(models.Driver.identity_card_no == upgrade_data.identity_card_no).first()
    if existing_id_card:
        raise HTTPException(status_code=400, detail="Số căn cước công dân đã tồn tại trên hệ thống.")

    return crud.create_driver_profile_for_existing_user(db, current_user.id, upgrade_data)



# --- ĐĂNG NHẬP (OAUTH2 FORM DÙNG CHO SWAGGER UI) ---
@router.post("/login", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Đăng nhập lấy Token bằng OAuth2 Form (Nhập SĐT hoặc Email vào ô username).
    Hỗ trợ nút Authorize 🔒 trực tiếp trên Swagger UI docs.
    """
    auth_result = crud.authenticate_user(db, identifier=form_data.username, password=form_data.password, login_as="customer")
    if not auth_result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập (SĐT/Email) hoặc mật khẩu không chính xác.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if len(auth_result) == 2 and auth_result[1] == "NOT_A_DRIVER":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản này chưa đăng ký làm Tài xế."
        )

    user, roles, active_role = auth_result
    access_token = security.create_access_token(data={"sub": str(user.id), "roles": roles, "active_role": active_role})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "roles": roles,
        "active_role": active_role,
        "user_id": user.id
    }


# --- ĐĂNG NHẬP (JSON BODY DÙNG CHO FRONTEND / APP) ---
@router.post("/login-json", response_model=schemas.Token)
def login_json(
    login_req: schemas.LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Đăng nhập lấy Token bằng JSON Body {"identifier": "...", "password": "...", "login_as": "customer/driver"}.
    """
    login_as = login_req.login_as or "customer"
    auth_result = crud.authenticate_user(db, identifier=login_req.identifier, password=login_req.password, login_as=login_as)
    
    if not auth_result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập (SĐT/Email) hoặc mật khẩu không chính xác.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if len(auth_result) == 2 and auth_result[1] == "NOT_A_DRIVER":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản này chưa đăng ký làm Tài xế. Vui lòng đăng ký trước!"
        )

    user, roles, active_role = auth_result
    access_token = security.create_access_token(data={"sub": str(user.id), "roles": roles, "active_role": active_role})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "roles": roles,
        "active_role": active_role,
        "user_id": user.id
    }


# --- XEM THÔNG TIN TÀI KHOẢN ĐANG ĐĂNG NHẬP ---
@router.get("/me", response_model=schemas.UserMeOut)
def read_users_me(
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lấy thông tin tài khoản hiện tại dựa vào JWT Access Token gửi ở Header Authorization: Bearer <token>.
    """
    roles = crud.get_user_roles(db, current_user.id)
    driver_profile = crud.get_driver(db, current_user.id)

    return {
        "id": current_user.id,
        "name": current_user.name,
        "phone": current_user.phone,
        "email": current_user.email,
        "rating": current_user.rating,
        "total_rides": current_user.total_rides,
        "roles": roles,
        "active_role": "driver" if driver_profile else "customer",
        "driver_profile": driver_profile
    }
