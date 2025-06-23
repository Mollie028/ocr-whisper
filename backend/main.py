from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import auth  # 🆕 匯入 auth 路由

app = FastAPI()

# CORS 設定（允許前端連線）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🧩 掛載路由
app.include_router(auth.router)

# ➕ 之後可以繼續加其他 router，例如：
# from backend.api import ocr, whisper, extract
# app.include_router(ocr.router)
# app.include_router(whisper.router)
# app.include_router(extract.router)

@app.get("/")
def root():
    return {"msg": "🚀 FastAPI 啟動成功"}
