from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 匯入所有 API 模組
from api import ocr, whisper, extract, auth

app = FastAPI()

# CORS 設定：允許前端跨域請求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 部署時可改為你的前端網址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊 API 路由
app.include_router(ocr.router)
app.include_router(whisper.router)
app.include_router(extract.router)
app.include_router(auth.router)

# 根目錄測試
@app.get("/")
def read_root():
    return {"message": "✅ 名片辨識系統已啟動"}

# 本地開發時使用：python main.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
