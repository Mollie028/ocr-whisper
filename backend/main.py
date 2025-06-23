from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os  # ✅ 補上 os 套件

# ✅ 改為從 backend 開始引入
from backend.api import auth, ocr, whisper, extract

app = FastAPI()

# CORS 設定，允許所有來源（你也可以自行限制 origins）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 可改為前端網址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由註冊
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(ocr.router, prefix="/ocr", tags=["ocr"])
app.include_router(whisper.router, prefix="/whisper", tags=["whisper"])
app.include_router(extract.router, prefix="/extract", tags=["extract"])

@app.get("/")
def root():
    return {"message": "OCR + Whisper API is running."}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
