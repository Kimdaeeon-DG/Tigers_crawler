# Node.js 베이스 이미지
FROM node:16

# 패키지 목록 업데이트
RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# pip 업그레이드 및 버전 확인
RUN python3 -m pip install --upgrade pip && \
    python3 --version && \
    pip3 --version

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

# 실행 명령
CMD ["node", "web/server.js"]
