import sys
import os

# 加入 backend/ 為模組根目錄，讓 import backend.xxx 能成功
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ✅ 引入 backend 底下的模組
from backend.api import auth, ocr, whisper, extract

app = FastAPI()

# CORS 設定：允許所有來源（你也可以自行限制 origins）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 可改為指定網址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由註冊
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(ocr.router, prefix="/ocr", tags=["ocr"])
app.include_router(whisper.router, prefix="/whisper", tags=["whisper"])
app.include_router(extract.router, prefix="/extract", tags=["extract"])

# 根目錄測試用
@app.get("/")
def root():
    return {"message": "OCR + Whisper API is running."}
