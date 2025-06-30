from faster_whisper import WhisperModel
import tempfile
import os

whisper_model = None

def initialize_whisper_model():
    global whisper_model
    if whisper_model is None:
        print("🚀 初始化 Whisper 模型（tiny）...")
        whisper_model = WhisperModel("tiny", compute_type="int8", device="cpu")
        print("✅ Whisper 模型初始化完成！")
    return whisper_model

def transcribe_audio(file):
    model = initialize_whisper_model()

    if hasattr(file, "file"):
        audio_bytes = file.file.read()
    else:
        audio_bytes = file.read()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        segments, _ = model.transcribe(tmp_path, beam_size=1)
        text = "".join([seg.text for seg in segments])
        return text.strip()
    finally:
        os.remove(tmp_path)
