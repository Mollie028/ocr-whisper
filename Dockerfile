FROM python:3.11

WORKDIR /app

# 安裝 PaddleOCR 與 Whisper 相關依賴
RUN apt-get update && apt-get install -y \
    libgl1 libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 \
    gcc build-essential python3-dev pkg-config \
    libssl-dev \
    wget \
    && apt-get clean

# 嘗試手動裝 libssl.so.1.1（從 Ubuntu 下載舊版本）
RUN wget http://security.ubuntu.com/ubuntu/pool/main/o/openssl1.1/libssl1.1_1.1.1f-1ubuntu2.22_amd64.deb && \
    dpkg -i libssl1.1_1.1.1f-1ubuntu2.22_amd64.deb && \
    rm libssl1.1_1.1.1f-1ubuntu2.22_amd64.deb

# 安裝 Python 套件
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt --no-deps
RUN pip install PyMuPDF==1.22.3
RUN pip install paddleocr==2.6.1.3 --no-deps

COPY . .

ENV PYTHONPATH=/app/backend
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
