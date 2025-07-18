from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.services.ocr_service import run_ocr
from backend.services.extract_service import extract_fields_from_llm
from backend.core.db import SessionLocal
from backend.models.user import Card
from datetime import datetime

router = APIRouter(prefix="/ocr", tags=["OCR 名片辨識"])

@router.post("/")
async def ocr_card(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        raise HTTPException(status_code=400, detail="請上傳 jpg、jpeg 或 png 格式圖片")

    db = SessionLocal()
    try:
        # OCR 處理
        text = await run_ocr(file)

        # 使用 LLM 萃取欄位
        fields = extract_fields_from_llm(text)

        # 建立 Card 物件，只傳入 DB 有的欄位
        card = Card(
            name=fields.get("name", "未知"),
            title=fields.get("title", "未知"),
            email=fields.get("email", "未知"),
            phone=fields.get("phone", "未知"),
            company_name=fields.get("company_name", "未知"),
            created_at=datetime.utcnow()  # 如果你的資料表有這欄位
        )

        db.add(card)
        db.commit()
        db.refresh(card)

        return {
            "message": "✅ OCR 成功，欄位已萃取並儲存",
            "record_id": card.id,
            "fields": fields,
            "raw_text": text
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"❌ 發生錯誤：{str(e)}")

    finally:
        db.close()
