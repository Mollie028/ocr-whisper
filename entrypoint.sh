#!/bin/bash

echo "✅ 啟動 OCR + Whisper API"

uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}
