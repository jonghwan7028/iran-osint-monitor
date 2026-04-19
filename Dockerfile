FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# 시스템 패키지 (psycopg 빌드용 최소)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq5 \
        curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Render 는 $PORT 환경변수로 바인딩 포트를 전달한다
ENV PORT=8000
EXPOSE 8000

# 프로덕션: workers 1 (SQLite/단일 DB 세션 기준), 공개 모드 기본 on
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
