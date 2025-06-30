FROM python:3.11

WORKDIR /app

# 安裝系統套件：讓 PyMuPDF 可以編譯
RUN apt-get update && apt-get install -y \
    libgl1 libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 \
    gcc build-essential python3-dev pkg-config \
    && apt-get clean

COPY requirements.txt .

RUN pip install PyMuPDF==1.22.3

RUN pip install --upgrade pip && pip install -r requirements.txt --no-deps

RUN pip install paddleocr==2.6.1.3


ENV PYTHONPATH=/app
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "backend"]
