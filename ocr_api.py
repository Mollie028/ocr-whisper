from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from paddleocr import PaddleOCR
from faster_whisper import WhisperModel
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ocr_model = PaddleOCR(use_angle_cls=True, lang='ch', det_db_box_thresh=0.3)
whisper_model = WhisperModel("small", device="cpu", compute_type="int8")

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": os.getenv("DB_PORT")
}

def get_conn():
    return psycopg2.connect(**DB_CONFIG)

def call_llama_and_update(text, record_id):
    prompt = (
        "你是一個專業資料萃取助手，請從以下文字中擷取出名片欄位，"
        "並以 JSON 格式回傳，key 名稱請使用：\n"
        "name, phone, email, title, company_name, address\n\n"
        "範例：\n"
        '{\n  "name": "王小明",\n  "phone": "0912-345-678",\n  "email": "test@example.com",\n'
        '  "title": "業務經理",\n  "company_name": "新光保險",\n  "address": "台北市中山區xx路xx號"\n}\n\n'
        "請從以下內容中擷取：\n" + text
    )

    llama_api = "https://api.together.xyz/v1/completions"
    headers = {
        "Authorization": f"Bearer {os.getenv('TOGETHER_API_KEY')}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "meta-llama/Llama-3-8b-chat-hf",
        "prompt": prompt,
        "max_tokens": 512,
        "temperature": 0.3,
    }

    try:
        res = requests.post(llama_api, headers=headers, json=body)
        parsed_text = res.json()["choices"][0]["text"].strip()
        start_idx = parsed_text.index("{")
        parsed_json = json.loads(parsed_text[start_idx:])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLaMA 解析失敗：{e}")

    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE business_cards
            SET name = %s, phone = %s, email = %s, title = %s, company_name = %s, address = %s
            WHERE id = %s
            """,
            (
                parsed_json.get("name"),
                parsed_json.get("phone"),
                parsed_json.get("email"),
                parsed_json.get("title"),
                parsed_json.get("company_name"),
                parsed_json.get("address"),
                record_id
            )
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"寫入資料庫失敗：{e}")

@app.post("/ocr")
async def ocr_endpoint(file: UploadFile = File(...), user_id: int = 1):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        result = ocr_model.ocr(img)
        text = "\n".join([line[1][0] for box in result for line in box])

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO business_cards (user_id, ocr_text) VALUES (%s, %s) RETURNING id", (user_id, text))
        record_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        call_llama_and_update(text, record_id)

        return {"id": record_id, "text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR 發生錯誤：{e}")

@app.post("/whisper")
async def whisper_endpoint(file: UploadFile = File(...), user_id: int = 1):
    try:
        contents = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        segments, _ = whisper_model.transcribe(
            tmp_path, language="zh", beam_size=1, vad_filter=True, max_new_tokens=440
        )
        text = " ".join([seg.text.strip() for seg in segments])

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO business_cards (user_id, ocr_text) VALUES (%s, %s) RETURNING id", (user_id, text))
        record_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        call_llama_and_update(text, record_id)

        return {"id": record_id, "text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Whisper 發生錯誤：{e}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
