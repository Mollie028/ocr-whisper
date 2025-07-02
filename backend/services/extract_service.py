import os
import json
import requests
from sqlalchemy.orm import Session
from backend.models.card import Card  # 確保這個 model 有對應欄位
from backend.core.db import get_db    # 若你有用 FastAPI 的 Depends 時會用到


def extract_fields_from_llm(text: str) -> dict:
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
                    "你是一個專業資料萃取助手，負責從名片 OCR 文字中找出聯絡資訊。"
                    "只回傳 JSON 格式，欄位包括 name, phone, email, title, company_name。"
                    "請勿使用虛構資料或範例。無資料請填 '未知'。"
                )
            },
            {
                "role": "user",
                "content": text
            }
        ],
        "temperature": 0.2,
        "max_tokens": 512
    }

    res = requests.post(llama_api, headers=headers, json=body)
    res.raise_for_status()
    parsed_text = res.json()["choices"][0]["message"]["content"].strip()

    # 只取出 {...} JSON 部分
    start = parsed_text.find("{")
    end = parsed_text.rfind("}") + 1
    return json.loads(parsed_text[start:end])


def save_extracted_fields_to_db(record_id: int, fields: dict, db: Session):
    card = db.query(Card).filter(Card.id == record_id).first()
    if not card:
        raise Exception(f"❌ 無法找到 id 為 {record_id} 的名片紀錄")
    
    card.name = fields.get("name")
    card.phone = fields.get("phone")
    card.email = fields.get("email")
    card.title = fields.get("title")
    card.company_name = fields.get("company_name")
    db.commit()
