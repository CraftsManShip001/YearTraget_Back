# Python 3.12 이미지 사용
FROM python:3.12

# 의존성 설치
RUN pip install --upgrade pip

# 시스템 의존성 설치 (필요한 경우만 사용)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# 로컬 파일을 컨테이너로 복사
COPY . /app

# requirements.txt에서 의존성 설치
RUN if [ -f "./requirements.txt" ]; then pip install -r requirements.txt; fi

# FastAPI 앱 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
