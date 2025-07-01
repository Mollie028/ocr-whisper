FROM python:3.11-buster
ENV DEBIAN_FRONTEND=noninteractive


RUN apt-get update && apt-get install -y \
    build-essential \
    libmupdf-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libfreetype6-dev \
    libwebp-dev \
    libopenjp2-7-dev \
    poppler-utils \
    libgl1-mesa-glx \
    libsm6 \
    libxext6 \
    pkg-config \
    cmake \
    zlib1g-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    liblcms2-dev \
    libxml2-dev \
    libxslt1-dev \
    libsndfile1-dev \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT 8000
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "$PORT"]
