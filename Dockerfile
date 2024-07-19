# 베이스 이미지로 Python 사용
FROM python:3.11.9

WORKDIR /app

# 필요 라이브러리 설치
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

# 애플리케이션 파일 복사
COPY . /app/

# 앱 실행
CMD ["python", "/app/app/server.py"]