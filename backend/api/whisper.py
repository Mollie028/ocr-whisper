from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.services.whisper_service import transcribe_audio # 確保這裡是 transcribe_audio

router = APIRouter()

@router.post("/") # 將路徑從 "/whisper" 改為 "/"
async def whisper(file: UploadFile = File(...)):
    try:
        # transcribe_audio 函數在 whisper_service.py 中設計為可以直接接收 UploadFile 物件
        result = transcribe_audio(file) # 直接傳入 file，不再需要 read() contents
        return {"message": "語音辨識成功", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ 語音辨識失敗：{str(e)}") # 優化錯誤訊息
