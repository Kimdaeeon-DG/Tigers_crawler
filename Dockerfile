# Python 베이스 이미지 사용
FROM python:3.9

# Node.js 설치
RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash - && \
    apt-get install -y nodejs

# Chrome 설치
RUN apt-get update && \
    apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# Python 요구사항 복사 및 설치
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Node.js 의존성 복사 및 설치
COPY web/package*.json web/
RUN cd web && npm install

# 나머지 파일 복사
COPY . .

# 포트 설정
EXPOSE 3000

# 환경 변수 설정
ENV NODE_ENV=production
ENV PORT=3000
ENV PYTHONUNBUFFERED=1

# 실행 명령
CMD ["node", "web/server.js"]
