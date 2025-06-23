from fastapi import FastAPI
from api import auth, ocr, whisper  # ← 加上 whisper
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS 設定（讓前端可跨域呼叫 API）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 可改成你的前端網址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由導入
app.include_router(auth.router, prefix="/api")
app.include_router(ocr.router, prefix="/api")
app.include_router(whisper.router, prefix="/api")  # ← 加這行

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
