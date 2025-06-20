from passlib.context import CryptContext

# 建立密碼加密的上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 密碼加密函式
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# 密碼驗證函式
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
