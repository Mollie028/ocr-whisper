FROM python:3.11-slim-buster

WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    libgl1 libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 \
    gcc build-essential python3-dev pkg-config curl \
    && apt-get clean

# 安裝 Python 套件
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install PyMuPDF==1.22.3

# 複製專案程式碼
COPY . .

# 設定 Python 路徑（可 import backend）
ENV PYTHONPATH=/app

# 對外開放 port
EXPOSE 8000

# 啟動 API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
