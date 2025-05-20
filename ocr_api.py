# ocr_api.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from paddleocr import PaddleOCR
from faster_whisper import WhisperModel
from PIL import Image
from sentence_transformers import SentenceTransformer
import numpy as np
import cv2
import io
import tempfile
import os
import uvicorn
import requests
import psycopg2
import json

app = FastAPI()

# 允許跨來源存取（給 Streamlit 用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化模型（使用輕量版）
ocr_model = PaddleOCR(use_angle_cls=True, lang='ch', det_db_box_thresh=0.3)
whisper_model = WhisperModel("small", device="cpu", compute_type="int8")
embed_model = SentenceTransformer('all-MiniLM-L6-v2')

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": int(os.getenv("DB_PORT", 5432))
}

def save_to_postgres(text, vector):
    try:
        conn = psycopg2.connect(**DB_CONFIG, sslmode='require')
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ocr_data (
                id SERIAL PRIMARY KEY,
                content TEXT,
                embedding VECTOR(384)
            );
        """)
        cur.execute("INSERT INTO ocr_data (content, embedding) VALUES (%s, %s)", (text, vector))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("❌ PostgreSQL 儲存失敗：", e)


@app.post("/ocr")
async def ocr_endpoint(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        result = ocr_model.ocr(img, cls=True)
        
        text = "\n".join([line[1][0] for box in result for line in box])
        return {"text": text}
    except Exception as e:
        return {"error": str(e)}

@app.post("/whisper")
async def whisper_endpoint(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        segments, _ = whisper_model.transcribe(
            tmp_path, language="zh", beam_size=1, vad_filter=True,
            max_new_tokens=440
        )
        text = " ".join([seg.text.strip() for seg in segments])
        text = cc.convert(text)
        return {"text": text}
    except Exception as e:
        return {"error": str(e)}
@app.post("/extract")
async def extract_fields(payload: dict):
    text = payload.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="Missing text")
        
# 路由 3: 欄位萃取（使用 LLaMA API）
@app.post("/extract")
async def extract_fields(payload: dict):
    text = payload.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="Missing text")

    # 可替換為自己的 LLaMA API
    llama_prompt = f"請從以下內容中萃取出欄位，回傳 JSON 格式：姓名、電話、公司、備註：\n{text}"
    llama_api = "https://api.together.xyz/v1/completions"
    headers = {
        "Authorization": f"Bearer {os.getenv('TOGETHER_API_KEY')}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "meta-llama/Llama-3-8b-chat-hf",
        "prompt": llama_prompt,
        "max_tokens": 300,
        "temperature": 0.7,
    }

    res = requests.post(llama_api, headers=headers, json=body)
    try:
        parsed = res.json()["choices"][0]["text"]
        return {"fields": parsed}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLaMA API 錯誤：{e}")

# 路由 4: 向量轉換
@app.post("/embed")
async def embed_text(payload: dict):
    note = payload.get("note", "")
    if not note:
        raise HTTPException(status_code=400, detail="Missing note text")
    vector = embed_model.encode(note).tolist()
    return {"vector": vector}

       

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # 預設 8000，部署時會抓環境變數
    uvicorn.run(app, host="0.0.0.0", port=port)

        

