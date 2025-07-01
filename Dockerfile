FROM python:3.11-slim-buster

WORKDIR /app

# 安裝系統依賴（包含 paddle、whisper 會用到的 libssl、影像處理等）
RUN apt-get update && apt-get install -y \
    libgl1 libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 \
    gcc build-essential python3-dev pkg-config curl libssl1.1 \
    && apt-get clean

# 複製 requirements.txt 並一次安裝所有套件（不要用 --no-deps）
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 複製整個專案
COPY . .

# 設定 PYTHONPATH（確保能匯入 backend 模組）
ENV PYTHONPATH=/app/backend

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
