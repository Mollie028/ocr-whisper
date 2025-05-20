# ocr_api.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from paddleocr import PaddleOCR
from faster_whisper import WhisperModel
from sentence_transformers import SentenceTransformer
from PIL import Image
import numpy as np
import cv2
import io
import tempfile
import os
import requests
import psycopg2
import json

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 模型初始化
ocr_model = PaddleOCR(use_angle_cls=True, lang='ch', det_db_box_thresh=0.3)
whisper_model = WhisperModel("small", device="cpu", compute_type="int8")
embed_model = SentenceTransformer('all-MiniLM-L6-v2')

def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT"),
        sslmode="require"
    )

# OCR：圖片轉文字
@app.post("/ocr")
async def ocr_endpoint(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        result = ocr_model.ocr(img, cls=True)

        raw_text = "\n".join([line[1][0] for box in result for line in box])
        vector = embed_model.encode(raw_text).tolist()

        # 欄位萃取
        llama_prompt = f"請從以下內容中萃取出欄位，回傳 JSON 格式：姓名、公司、電話、職稱、Email、地址：\n{raw_text}"
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
        llama_res = requests.post(llama_api, headers=headers, json=body)
        parsed_json = json.loads(llama_res.json()["choices"][0]["text"])

        # 儲存 DB
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO business_cards (
                user_id, name, company_name, phone, email, title, ocr_text, ocr_vector
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                1,  # 測試 user_id
                parsed_json.get("姓名", ""),
                parsed_json.get("公司", ""),
                parsed_json.get("電話", ""),
                parsed_json.get("Email", ""),
                parsed_json.get("職稱", ""),
                raw_text,
                vector
            )
        )
        conn.commit()
        cur.close()
        conn.close()

        return {"text": raw_text, "fields": parsed_json}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Whisper：語音轉文字
@app.post("/whisper")
async def whisper_endpoint(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        segments, _ = whisper_model.transcribe(
            tmp_path, language="zh", beam_size=1, vad_filter=True, max_new_tokens=440
        )
        text = " ".join([seg.text.strip() for seg in segments])
        vector = embed_model.encode(text).tolist()

        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO voice_notes (user_id, transcribed_text, transcribed_vector)
            VALUES (%s, %s, %s)
            """,
            (1, text, vector)
        )
        conn.commit()
        cur.close()
        conn.close()

        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 測試欄位萃取（獨立）
@app.post("/extract")
async def extract_fields(payload: dict):
    text = payload.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="Missing text")

    llama_prompt = f"請從以下內容中萃取出欄位，回傳 JSON 格式：姓名、公司、電話、職稱、Email、地址：\n{text}"
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
        parsed_json = json.loads(parsed)
        return {"fields": parsed_json}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLaMA API 錯誤：{e}")
