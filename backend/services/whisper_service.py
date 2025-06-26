# backend/services/whisper_service.py
import os
import tempfile
from faster_whisper import WhisperModel

# 宣告一個變數來存放模型，初始為 None
whisper_model_instance = None

def initialize_whisper_model():
    global whisper_model_instance
    if whisper_model_instance is None:
        print("🚀 初始化 Faster-Whisper 模型...")
        whisper_model_instance = WhisperModel("tiny", compute_type="int8")
        print("✅ Faster-Whisper 模型初始化完成。")
    return whisper_model_instance

def transcribe_audio(file):
    model = initialize_whisper_model() # 這裡現在會取得初始化過後的模型

    if hasattr(file, "file"):
        audio_bytes = file.file.read()
    else:
        audio_bytes = file

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        segments, _ = model.transcribe(tmp_path, beam_size=5)
        text = " ".join([seg.text for seg in segments])
        return text.strip()
    finally:
        os.remove(tmp_path)
