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

def clean_ocr_text(text):
    lines = text.split("\n")
    cleaned = []
    for line in lines:
        line = line.strip()
        if line and not any(x in line.lower() for x in ["fax", "傳真", "www", "網址"]):
            cleaned.append(line)
    return "\n".join(cleaned)

def call_llama_and_update(text, record_id):
    print("📄 傳送給 LLaMA 的 OCR 內容：\n", text)
    
    llama_api = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.getenv('TOGETHER_API_KEY')}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "meta-llama/Llama-3-8b-chat-hf",
        "messages": [
            {
                "role": "system",
                "content": (
                    "你是一個專業資料萃取助手，專門負責從中文名片中提取聯絡資訊。"
                    "請你只回傳 JSON 格式，不要有任何額外文字或說明。"
                    "欄位包括：name, phone, email, title, company_name。"
                    "若無法確定欄位內容，請填入 '未知'，但請勿留空。"
                )
            },
            {
                "role": "user",
                "content": (
                    "以下是名片 OCR 辨識結果，請根據內容回傳格式如下的 JSON："
                    "{\"name\":\"王小明\",\"phone\":\"0912-345-678\",\"email\":\"test@example.com\","
                    "\"title\":\"業務經理\",\"company_name\":\"新光保險\"}"
                    f"\n{text}"
                )
            }
        ],
        "temperature": 0.2,
        "max_tokens": 512
    }


    try:
        res = requests.post(llama_api, headers=headers, json=body)
        res.raise_for_status()
        res_json = res.json()

        parsed_text = res_json["choices"][0]["message"]["content"].strip()
        print("🧠 LLaMA 回應：", parsed_text)
        
        start_idx = parsed_text.find("{")
        if start_idx == -1:
            raise ValueError("LLaMA 回傳內容中找不到 JSON 起始符號 '{'")
        parsed_json = json.loads(parsed_text[start_idx:])
        if not any(parsed_json.values()):
            raise HTTPException(status_code=400, detail="⚠️ LLaMA 回傳的所有欄位為空，可能是無法辨識。")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLaMA 解析失敗：{e}")
    

    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE business_cards
            SET name = %s, phone = %s, email = %s, title = %s, company_name = %s
            WHERE id = %s
            """,
            (
                parsed_json.get("name"),
                parsed_json.get("phone"),
                parsed_json.get("email"),
                parsed_json.get("title"),
                parsed_json.get("company_name"),
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

        lines = []
        for box in result:
            for line in box:
                text_piece = line[1][0].strip()
                if text_piece and not any(c in text_piece.lower() for c in ["www", "fax", "網址", "傳真"]):
                    lines.append(text_piece)
        cleaned_text = "\n".join(lines)

        print("🖼️ OCR 辨識結果：", cleaned_text)

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO business_cards (user_id, ocr_text) VALUES (%s, %s) RETURNING id", (user_id, cleaned_text))
        record_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        call_llama_and_update(cleaned_text, record_id)

        return {"id": record_id, "text": cleaned_text}
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
