# Python 3.13 이미지 사용
FROM python:3.13

# 의존성 설치
RUN pip install --upgrade pip
RUN pip install --no-cache-dir fastapi uvicorn

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
# 작업 디렉토리 설정
WORKDIR /app

# 로컬 파일을 컨테이너로 복사
COPY ./main.py /app/main.py
COPY ./data /app/data


# main.py 실행
CMD ["python", "/app/main.py"]
