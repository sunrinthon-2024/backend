FROM python:3.11.9

# 작업 디렉토리를 설정
WORKDIR /code

# 필요 라이브러리 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 파일 복사
COPY . .

# 앱 실행
CMD ["python", "app/server.py"]