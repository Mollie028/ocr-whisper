from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from backend.core.db import get_db
from backend.models.user import User, UserCreate, UserLogin, UserOut
from backend.core.security import get_password_hash, verify_password, create_access_token
from backend.services.user_service import get_user_by_username
from pydantic import BaseModel
import traceback

router = APIRouter()

class UpdateUserRole(BaseModel):
    username: str
    is_admin: bool

class UpdatePassword(BaseModel):
    username: str
    new_password: str

class UpdateNoteRequest(BaseModel):
    username: str
    note: str

class DeactivateUserRequest(BaseModel):
    username: str

# ✅ 註冊
@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        if get_user_by_username(db, user.username):
            return JSONResponse(status_code=400, content={"message": "⚠️ 帳號已存在"})

        hashed_password = get_password_hash(user.password)
        new_user = User(
            username=user.username,
            password_hash=hashed_password,
            company_name=user.company_name,
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

    except Exception as e:
        print(traceback.format_exc())
        return JSONResponse(status_code=500, content={"message": f"🚨 系統內部錯誤：{str(e)}"})

# ✅ 登入
@router.post("/login")
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    try:
        print("⚙️ 登入開始", flush=True)

        user = get_user_by_username(db, login_data.username)
        print("👤 查詢結果：", user, flush=True)

        if not user or not verify_password(login_data.password, user.password_hash):
            print("❌ 帳號或密碼錯誤", flush=True)
            raise HTTPException(status_code=401, detail="❌ 帳號或密碼錯誤")
        if not user.is_active:
            print("⛔️ 帳號被停用", flush=True)
            raise HTTPException(status_code=403, detail="⛔️ 帳號已被停用，請聯絡管理員")

        token = create_access_token({"sub": user.username, "is_admin": user.is_admin})
        print("✅ 登入成功，Token：", token, flush=True)

        return {
            "access_token": token,
            "token_type": "bearer",
            "is_admin": user.is_admin,
            "company_name": user.company_name,
            "role": "admin" if user.is_admin else "user"
        }
    except Exception as e:
        import traceback
        print("❌ login 錯誤：", traceback.format_exc(), flush=True)
        raise HTTPException(status_code=500, detail="🚨 系統內部錯誤")




# ✅ 取得所有使用者（可依公司過濾）
@router.get("/get_users")
def get_users(company_name: str = "", db: Session = Depends(get_db)):
    try:
        query = db.query(User)
        if company_name:
            query = query.filter(User.company_name == company_name)
        users = query.all()
        return [
            {
                "id": u.id,
                "username": u.username,
                "is_admin": u.is_admin,
                "company_name": u.company_name,
                "note": getattr(u, "note", None) if hasattr(u, "note") else None,
                "is_active": getattr(u, "is_active", True) if hasattr(u, "is_active") else True,
            }
            for u in users
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ 系統錯誤：{str(e)}")

# ✅ 更新角色權限
@router.post("/update_role")
def update_user_role(data: UpdateUserRole, db: Session = Depends(get_db)):
    user = get_user_by_username(db, data.username)
    if not user:
        raise HTTPException(status_code=404, detail="使用者不存在")
    user.is_admin = data.is_admin
    db.commit()
    return {"message": "✅ 使用者權限已更新"}

# ✅ 更新密碼
@router.put("/update_password")
def update_password(data: UpdatePassword, db: Session = Depends(get_db)):
    user = get_user_by_username(db, data.username)
    if not user:
        raise HTTPException(status_code=404, detail="使用者不存在")
    user.password_hash = get_password_hash(data.new_password)
    db.commit()
    return {"message": "✅ 密碼更新成功"}

# ✅ 更新備註
@router.post("/update_note")
def update_note(data: UpdateNoteRequest, db: Session = Depends(get_db)):
    user = get_user_by_username(db, data.username)
    if not user:
        raise HTTPException(status_code=404, detail="使用者不存在")
    if hasattr(user, "note"):
        user.note = data.note
        db.commit()
        return {"message": "✅ 備註已更新"}
    else:
        raise HTTPException(status_code=400, detail="⚠️ 備註功能未啟用，請聯絡管理員")

# ✅ 註銷帳號
@router.post("/deactivate_user")
def deactivate_user(data: DeactivateUserRequest, db: Session = Depends(get_db)):
    user = get_user_by_username(db, data.username)
    if not user:
        raise HTTPException(status_code=404, detail="使用者不存在")
    if hasattr(user, "is_active"):
        user.is_active = False
        db.commit()
        return {"message": "⛔️ 帳號已註銷"}
    else:
        raise HTTPException(status_code=400, detail="⚠️ 此資料庫不支援帳號註銷功能")
