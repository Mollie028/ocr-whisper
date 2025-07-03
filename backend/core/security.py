from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt

# 建立雜湊器
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Secret key 建議用 env 讀取（這裡先寫死）
SECRET_KEY = "mysecretkey123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 小時

# ✅ 密碼雜湊
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# ✅ 密碼驗證
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# ✅ 建立 JWT token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
