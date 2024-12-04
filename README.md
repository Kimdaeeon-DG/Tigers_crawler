# Tigers crawler 구현
>대구대학교 타이거즈 화면 성적을 음성 혹은 텍스트로 반환해주는 프로그램

[성적 조회 사이트](https://tg.mydu.duckdns.org/)

# 개발환경
>python,
>nodeJs,
>JavaScript,
>HTML

# selenium 실행을 위한 환경 설정
```bash
brew install python
pip install selenium
```

### 실행 방법
```bash
python main.py
```

# web 실행을 위한 환경변수 설정
```bash
npm init -y
npm install express bcryptjs express-session body-parser
npm install mysql2 sequelize
```

### DB 설정
```sql
CREATE DATABASE mydatabase;
CREATE USER 'myuser'@'localhost' IDENTIFIED BY 'mypassword';
GRANT ALL PRIVILEGES ON mydatabase.* TO 'myuser'@'localhost';
FLUSH PRIVILEGES;
```

### 이메일 관련 패키지
```bash
npm install nodemailer crypto
```

### 실행 방법
```bash
node server.js
```

### API_KEY 설정 방법
```bash
pip install python-dotenv
vim .env
```

### .env 파일 세팅
```bash
# 띄어쓰기 없이 작성하여야함
# .env
key="본인의 API_KEY"
```

### Todo
- 유저 정보 입력받는것 처리
- 에러 핸들링
