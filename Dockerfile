FROM python:3.11

WORKDIR /app

# 安裝 PyMuPDF 相關依賴
RUN apt-get update && apt-get install -y \
    libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 \
    gcc build-essential python3-dev pkg-config \
 && apt-get clean

COPY requirements.txt .

RUN pip install PyMuPDF==1.22.3
RUN pip install --upgrade pip && pip install -r requirements.txt --no-deps
RUN pip install paddleocr==2.6.1.3 --no-deps
RUN echo 
ENV PYTHONPATH=/app
EXPOSE 8000

# ✅ 正確啟動指令：用 main.py 而不是 backend.main
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
