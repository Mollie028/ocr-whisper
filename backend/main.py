import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 模組匯入：依照專案結構 backend/api/*
from backend.api import auth, ocr, whisper, extract

app = FastAPI()

# CORS 設定（允許前端跨網域請求）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 部署完成後可改為前端網址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 路由註冊
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(ocr.router, prefix="/ocr", tags=["ocr"])
app.include_router(whisper.router, prefix="/whisper", tags=["whisper"])
app.include_router(extract.router, prefix="/extract", tags=["extract"])

# 根目錄健康檢查
@app.get("/")
def root():
    return {"message": "✅ OCR + Whisper API is running."}

# Railway 執行進入點
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)
