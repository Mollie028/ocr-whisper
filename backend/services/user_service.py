from sqlalchemy.orm import Session
from backend.models.user import User, UserCreate
from backend.core.security import get_password_hash, verify_password


# 查詢使用者 by username
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


# 建立新使用者（註冊）
def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)

    # 根據角色設定權限欄位（視資料表結構調整）
    is_admin = user.role == "admin"
    # 若你的資料表有 can_view_all 欄位，才打開這行
    # can_view_all = user.role in ["admin", "viewer"]

    db_user = User(
        username=user.username,
        password_hash=hashed_password,  # 與資料庫欄位一致
        company_name=user.company_name,
        role=user.role,
        is_admin=is_admin,
        is_active=True,  # 預設帳號啟用
        note=None
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# 登入驗證
def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


# 撈出所有使用者（給管理員帳號管理頁）
def get_all_users(db: Session):
    return db.query(User).all()
