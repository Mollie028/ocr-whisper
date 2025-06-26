#!/bin/bash

echo "🚀 Running entrypoint.sh"

export PYTHONPATH=/app  # ✅ 這行一定要有
exec uvicorn backend.main:app --host=0.0.0.0 --port=8000 --reload
