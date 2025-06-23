from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.services.whisper_service import transcribe_audio  

router = APIRouter()

@router.post("/whisper")
async def whisper(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        result = transcribe_audio_file(contents)
        return {"message": "語音辨識成功", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
