from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.core.db import get_db
from backend.models.user import User, UserCreate, UserLogin, UserOut
from backend.core.security import get_password_hash, verify_password, create_access_token

router = APIRouter()

@router.post("/register", response_model=UserOut)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # 檢查使用者是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="❌ 使用者已存在")

    # 建立新使用者
    hashed_pw = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        password_hash=hashed_pw,
        company_name=user_data.company_name,
        is_admin=False,
        can_view_all=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login")
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == login_data.username).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="❌ 使用者名稱或密碼錯誤")

    # 建立 JWT token，含 is_admin 權限
    token = create_access_token(data={
        "sub": user.username,
        "is_admin": user.is_admin
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "is_admin": user.is_admin
    }
