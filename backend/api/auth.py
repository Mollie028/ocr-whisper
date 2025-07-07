from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from backend.core.db import get_db
from backend.models.user import User, UserCreate, UserLogin, UserOut
from backend.core.security import get_password_hash, verify_password, create_access_token
import traceback
router = APIRouter()

# ✅ 註冊新使用者
@router.post("/register", response_model=UserOut)
def register(user_data: UserCreate, db: Session = Depends(get_db)) -> UserOut:
    try:
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="❌ 此帳號已存在，請換一個")

        hashed_pw = get_password_hash(user_data.password)

        # ✅ 加入 company_name 預設空字串處理
        company_name = user_data.company_name or ""

        new_user = User(
            username=user_data.username,
            password_hash=hashed_pw,
            company_name=company_name,
            is_admin=(user_data.role == "admin"),
            can_view_all=(user_data.role == "admin")
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    except Exception as e:
        print("❌ 註冊錯誤：", traceback.format_exc())
        return JSONResponse(status_code=500, content={"message": "🚨 系統內部錯誤"})


# ✅ 使用者登入
@router.post("/login")
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == login_data.username).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="❌ 帳號或密碼錯誤")

    token = create_access_token(data={
        "sub": user.username,
        "is_admin": user.is_admin
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "is_admin": user.is_admin
    }


@router.get("/get_users")
def get_users(db: Session = Depends(get_db)):
    try:
        users = db.query(User).all()
        return [{"id": u.id, "username": u.username, "is_admin": u.is_admin} for u in users]
    except Exception as e:
        print("❌ 錯誤追蹤：", traceback.format_exc())  # 將完整錯誤印出
        raise HTTPException(status_code=500, detail=f"❌ 系統錯誤：{str(e)}")

