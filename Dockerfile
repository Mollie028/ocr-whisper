FROM python:3.11-slim

WORKDIR /app

# 安裝系統相依套件（包含模型需要的 lib）
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && apt-get clean

# 安裝 Python 套件
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 複製所有程式碼
COPY . .
RUN chmod +x entrypoint.sh


# 設定 PYTHONPATH 讓 FastAPI 能正確匯入 backend 資料夾的模組
ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["bash", "entrypoint.sh"]



