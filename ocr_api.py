from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.openapi.utils import get_openapi

from backend.core.security import create_access_token, SECRET_KEY, ALGORITHM
from backend.schemas.user import UserCreate, UserLogin, Token
from jose import jwt
from paddleocr import PaddleOCR
from faster_whisper import WhisperModel
from PIL import Image
import numpy as np
import tempfile
import os
import io

# ───── 載入模型（正式部署）─────
ocr_model = PaddleOCR(use_angle_cls=True, lang='ch', det_db_box_thresh=0.3)
whisper_model = WhisperModel("small", device="cpu", compute_type="int8")

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
        description="正式版（雲端部署）",
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

# ───── 登入／使用者資訊 ─────

@app.post("/register", response_model=Token)
async def register(user: UserCreate):
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/login", response_model=Token)
async def login(user: UserLogin):
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me")
async def read_current_user(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username: str = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="無效的 token")
    return {
        "username": username,
        "role": "admin" if username == "testuser" else "user"
    }

# ───── /ocr：圖片轉文字 ─────

@app.post("/ocr")
async def ocr_endpoint(file: UploadFile = File(...)):
    if not ocr_model:
        raise HTTPException(status_code=503, detail="OCR 模型未載入")

    image = await file.read()
    image_np = np.array(Image.open(io.BytesIO(image)).convert("RGB"))
    result = ocr_model.ocr(image_np, cls=True)
    texts = [line[1][0] for line in result[0]]
    return {"text": "\n".join(texts)}

# ───── /whisper：語音轉文字 ─────

@app.post("/whisper")
async def whisper_endpoint(file: UploadFile = File(...)):
    if not whisper_model:
        raise HTTPException(status_code=503, detail="Whisper 模型未載入")

    audio = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        temp_audio.write(audio)
        temp_audio_path = temp_audio.name

    segments, _ = whisper_model.transcribe(temp_audio_path, beam_size=5)
    os.remove(temp_audio_path)

    text_result = " ".join([seg.text for seg in segments])
    return {"text": text_result}

# ───── /extract：模擬欄位萃取 ─────

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

# ───── 本地執行入口（開發用）─────

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
