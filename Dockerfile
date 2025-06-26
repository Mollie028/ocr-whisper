FROM python:3.11-slim

WORKDIR /app

# 安裝必要套件
RUN apt-get update && apt-get install -y \
    libgl1 libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 && apt-get clean

# 安裝 Python 套件
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 複製所有程式碼
COPY . .

# 設定 PYTHONPATH，確保 FastAPI 能讀到 backend
ENV PYTHONPATH=/app

# 明確開放 port 8000
EXPOSE 8000

# 直接使用 uvicorn 啟動，不經過 bash
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
