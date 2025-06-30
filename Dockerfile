FROM python:3.11-slim-buster

WORKDIR /app

# 安裝 PaddleOCR 與 Whisper 所需依賴（包含 libssl1.1）
RUN apt-get update && apt-get install -y \
    libgl1 libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 \
    gcc build-essential python3-dev pkg-config \
    libssl1.1 \
    && apt-get clean

# 安裝 Python 套件
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt --no-deps
RUN pip install PyMuPDF==1.22.3
RUN pip install paddleocr==2.6.1.3
RUN pip install httpx opt_einsum
RUN pip install astor

COPY . .

ENV PYTHONPATH=/app/backend
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
