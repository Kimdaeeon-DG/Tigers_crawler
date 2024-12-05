# Node.js 및 Python이 설치된 기본 이미지 사용
FROM nikolaik/python-nodejs:latest

# 작업 디렉토리 설정
WORKDIR /app

# Chrome 및 ChromeDriver 설치
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지 설치를 위한 requirements.txt 복사 및 설치
COPY requirements.txt .
RUN pip install -r requirements.txt

# Node.js 패키지 설치를 위한 package.json 복사 및 설치
COPY web/package*.json web/
RUN cd web && npm install

# 나머지 소스 코드 복사
COPY . .

# 환경 변수 설정
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV NODE_ENV=production
ENV PORT=3000
ENV PYTHONUNBUFFERED=1

# Chrome 설정
ENV CHROME_OPTIONS="--headless --disable-gpu --no-sandbox --disable-dev-shm-usage"

# 포트 노출
EXPOSE 3000

# 애플리케이션 실행
CMD ["node", "web/server.js"]
