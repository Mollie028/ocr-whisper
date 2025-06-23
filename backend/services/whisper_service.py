import os
import tempfile
from faster_whisper import WhisperModel

tiny_model = WhisperModel("tiny", compute_type="int8")


def transcribe_audio(file):
    """
    將語音檔案轉換為逐字稿文字。
    支援 file 為 FastAPI 的 UploadFile 或 Streamlit 傳來的 bytes。
    """
    # 判斷是否為 UploadFile（FastAPI 傳送），還是 bytes（Streamlit 傳送）
    if hasattr(file, "file"):
        audio_bytes = file.file.read()
    else:
        audio_bytes = file

    # 將音訊寫入暫存檔
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        segments, _ = tiny_model.transcribe(tmp_path, beam_size=5)
        text = " ".join([seg.text for seg in segments])
        return text.strip()
    finally:
        os.remove(tmp_path)
