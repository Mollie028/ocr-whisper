from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.services.ocr_service import run_ocr
from backend.services.extract_service import extract_fields_from_llm
from backend.core.db import SessionLocal
from backend.models.user import Card  # Card 模型照你原本放在 user.py 裡
from datetime import datetime

router = APIRouter(prefix="/ocr", tags=["OCR 名片辨識"])

@router.post("/")
async def ocr_card(file: UploadFile = File(...)):
    # 1. 驗證檔案格式
    if not file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        raise HTTPException(status_code=400, detail="請上傳 jpg、jpeg 或 png 格式圖片")

    db = SessionLocal()
    try:
        # 2. 執行 OCR
        text = await run_ocr(file)

        # 3. 使用 LLM 萃取欄位
        fields = extract_fields_from_llm(text)

        # 4. 建立 Card 物件（不包含 image_url 和 created_at）
        card = Card(
            name=fields.get("name", "未知"),
            phone=fields.get("phone", "未知"),
            email=fields.get("email", "未知"),
            title=fields.get("title", "未知"),
            company_name=fields.get("company_name", "未知")
        )
        db.add(card)
        db.commit()
        db.refresh(card)

        # 5. 回傳結果
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
