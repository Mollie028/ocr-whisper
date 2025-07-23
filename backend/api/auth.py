from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.core.db import get_db
from backend.models.user import User, UserCreate, UserLogin, UserOut, UserUpdate
from backend.core.security import get_password_hash, verify_password, create_access_token, get_current_user
from backend.services.user_service import get_user_by_username, get_all_users, get_user_by_id
import traceback

router = APIRouter()

# ✅ 註冊
@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="⚠️ 帳號已存在")
    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        password_hash=hashed_password,
        company_name=user.company_name or "",
        is_admin=user.is_admin or False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "id": new_user.id,
        "username": new_user.username,
        "is_admin": new_user.is_admin
    }

# ✅ 登入
@router.post("/login")
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = get_user_by_username(db, login_data.username)
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="❌ 帳號或密碼錯誤")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="⛔️ 帳號已被停用")
    
    token = create_access_token({"sub": user.username, "is_admin": user.is_admin})
    return {
        "access_token": token,
        "token_type": "bearer",
        "is_admin": user.is_admin,
        "company_name": user.company_name,
        "role": "admin" if user.is_admin else "user"
    }

# ✅ 使用者列表
@router.get("/users", response_model=list[UserOut])
def get_users(db: Session = Depends(get_db)):
    try:
        users = get_all_users(db)
        return users
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="🚨 系統內部錯誤")

# ✅ 更新使用者基本資料
@router.put("/update_user/{user_id}")
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        user = get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="找不到使用者")

        if current_user.id != user.id and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="⛔️ 權限不足")
        if user.is_admin and current_user.id != user.id:
            raise HTTPException(status_code=403, detail="⛔️ 無法修改其他管理員")

        user.note = user_update.note or ""
        user.is_admin = bool(user_update.is_admin)
        user.is_active = bool(user_update.is_active)

        db.commit()
        db.refresh(user)

        return {
            "message": "✅ 使用者資料已更新",
            "user_id": user.id,
            "username": user.username
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="🚨 系統內部錯誤")

# ✅ 更新密碼 API
class PasswordUpdateRequest(BaseModel):
    new_password: str
    old_password: str | None = None

@router.put("/update_user_password/{user_id}")
def update_user_password(
    user_id: int,
    pwd_update: PasswordUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        user = get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="找不到使用者")

        if current_user.id != user.id and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="⛔️ 沒有權限修改他人密碼")

        if current_user.id == user.id:
            if not pwd_update.old_password or not verify_password(pwd_update.old_password, user.password_hash):
                raise HTTPException(status_code=401, detail="舊密碼錯誤")

        user.password_hash = get_password_hash(pwd_update.new_password)
        db.commit()

        return {"message": "✅ 密碼更新成功"}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="🚨 密碼更新失敗")
