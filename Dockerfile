FROM python:3.9-bullseye

WORKDIR /app

# 安裝必要套件（libgl1 等用於 PaddleOCR）
RUN apt-get update && apt-get install -y \
    libgl1 libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 \
    libopenblas-dev \
    gcc build-essential python3-dev pkg-config curl \
    && apt-get clean

# 安裝 Python 套件
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt --no-cache-dir
RUN pip install PyMuPDF==1.22.3

COPY . .

# 設定 Python 模組路徑
ENV PYTHONPATH=/app/backend

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
