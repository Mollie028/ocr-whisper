from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2PasswordBearer
from backend.core.security import get_password_hash, verify_password, create_access_token, SECRET_KEY, ALGORITHM
from backend.schemas.user import UserCreate, UserLogin, Token
from jose import JWTError, jwt

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import numpy as np
import cv2
import io
import tempfile
import os
import requests
import json
import socket

# ───── Debug DNS（僅顯示，不實際連線）─────
print("→ DEBUG: DB_HOST =", os.getenv("DB_HOST"))
try:
    ip = socket.gethostbyname(os.getenv("DB_HOST") or "")
    print(f"→ DEBUG: DNS OK, {os.getenv('DB_HOST')} → {ip}")
except Exception as e:
    print(f"→ DEBUG: DNS ERROR resolving {os.getenv('DB_HOST')}: {e}")
# ──────────────────────────────

# ───── 初始化 App ─────
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# ➕ Swagger UI 支援 Bearer Token
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="AI 名片辨識與語音備註系統",
        version="1.0.0",
        description="Demo 測試版，不連接資料庫",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"OAuth2PasswordBearer": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
# ──────────────────────────────

# ───── 模型控制變數 ─────
SKIP_MODEL_LOAD = os.getenv("SKIP_MODEL_LOAD", "false").lower() == "true"
if not SKIP_MODEL_LOAD:
    from paddleocr import PaddleOCR
    from faster_whisper import WhisperModel
    ocr_model = PaddleOCR(use_angle_cls=True, lang='ch', det_db_box_thresh=0.3)
    whisper_model = WhisperModel("small", device="cpu", compute_type="int8")
else:
    ocr_model = None
    whisper_model = None
# ──────────────────────

@app.post("/register", response_model=Token)
async def register(user: UserCreate):
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/login", response_model=Token)
async def login(user: UserLogin):
    print("🔑 DEBUG: SECRET_KEY used in login:", SECRET_KEY)  
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me")
async def read_current_user(token: str = Depends(oauth2_scheme)):
    from jose import jwt
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username: str = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="無效的 token")

    return {
        "username": username,
        "role": "admin" if username == "testuser" else "user"  
    }

        
@app.post("/ocr")
async def ocr_endpoint(file: UploadFile = File(...)):
    if not ocr_model:
        raise HTTPException(status_code=503, detail="OCR 模型未載入")
    return {"id": 123, "text": "這是測試用的 OCR 回傳文字"}

@app.post("/whisper")
async def whisper_endpoint(file: UploadFile = File(...)):
    if not whisper_model:
        raise HTTPException(status_code=503, detail="Whisper 模型未載入")
    return {"id": 456, "text": "這是測試用的語音文字"}

@app.post("/extract")
async def extract_fields(payload: dict):
    text = payload.get("text", "")
    record_id = payload.get("id", 0)
    if not text or not record_id:
        raise HTTPException(status_code=400, detail="❌ 缺少文字或 ID")
    return {
        "id": record_id,
        "fields": {
            "name": "王小明",
            "phone": "0912-345-678",
            "email": "test@example.com",
            "title": "工程師",
            "company_name": "測試公司"
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
