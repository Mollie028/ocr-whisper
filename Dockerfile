FROM python:3.11-slim

# 建立工作目錄
WORKDIR /app

# 安裝必要的系統套件（libgl1 給 OpenCV 用）
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 複製 requirements.txt 並安裝 Python 套件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製全部程式碼進入容器
COPY . /app

# 設定 PYTHONPATH，讓 FastAPI 可找到 backend 模組
ENV PYTHONPATH=/app

# 啟動 FastAPI 應用
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
