const express = require('express');
const session = require('express-session');
const bodyParser = require('body-parser');
const { execFile } = require('child_process');
const path = require('path');

const app = express();
const PORT = 3001;

app.use(bodyParser.urlencoded({ extended: true }));
app.use(session({
  secret: 'mysecret',
  resave: false,
  saveUninitialized: true
}));

app.use(express.static('public'));

// 로그아웃 라우트
app.post('/logout', (req, res) => {
  if (!req.session) {
    return res.json({ success: true });  // 이미 로그아웃 상태
  }
  
  // 세션 제거
  req.session.destroy((err) => {
    if (err) {
      console.error('Error destroying session:', err);
      return res.status(500).json({ 
        success: false, 
        error: '세션 제거 중 오류가 발생했습니다' 
      });
    }
    res.json({ success: true });
  });
});

// 로그인 페이지로 이동
app.get('/login', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'login.html'));
});

// 로그인 요청 처리
app.post('/login', async (req, res) => {
  const { username, password } = req.body;

  // Python 스크립트로 로그인 검증만 수행
  const scriptPath = path.join(__dirname, '..', 'main.py');
  const pythonPath = 'python3';

  execFile(pythonPath, [
    scriptPath,
    '--verify-login',  // 로그인 검증 모드
    username,
    password
  ], (error, stdout, stderr) => {
    if (error) {
      console.error('Error:', error);
      console.error('Stderr:', stderr);
      
      // 로그인 실패 메시지 확인
      if (stderr.includes('비밀번호 오 입력횟수')) {
        const match = stderr.match(/비밀번호 오 입력횟수 : \((\d+)\)/);
        const count = match ? match[1] : '알 수 없음';
        return res.redirect('/login?error=' + encodeURIComponent(`비밀번호 오 입력횟수: (${count})\n5회 이상 입력 오류 시 로그인이 제한되며\n비밀번호 초기화 후 로그인이 가능합니다.`));
      } else if (stderr.includes('아이디 또는 비밀번호가 맞지 않습니다')) {
        return res.redirect('/login?error=' + encodeURIComponent('아이디 또는 비밀번호가 맞지 않습니다.'));
      }
      
      return res.redirect('/login?error=' + encodeURIComponent('로그인 중 오류가 발생했습니다.'));
    }

    // 로그인 성공
    req.session.username = username;
    req.session.password = password;
    req.session.gradeData = {};  // 성적 데이터를 저장할 객체 초기화
    res.redirect('/dashboard');
  });
});

// 대시보드 페이지로 이동
app.get('/dashboard', (req, res) => {
  const username = req.session.username;
  const password = req.session.password;

  if (!username || !password) {
    return res.redirect('/login');
  }

  res.sendFile(path.join(__dirname, 'public', 'dashboard.html'));
});

// 선택 항목 제출 처리
app.post('/submit-selection', (req, res) => {
  const { year, semester } = req.body;
  const username = req.session.username;
  const password = req.session.password;

  if (!username || !password) {
    return res.status(400).send('User not logged in');
  }

  // 세션에 저장된 데이터가 있는지 확인
  const cacheKey = `${year}-${semester}`;
  if (req.session.gradeData && req.session.gradeData[cacheKey]) {
    console.log('캐시된 데이터 사용:', cacheKey);
    
    // 캐시된 데이터와 음성 파일 경로 반환
    const cachedData = req.session.gradeData[cacheKey];
    if (!cachedData.audioPath || !require('fs').existsSync(path.join(__dirname, 'public', cachedData.audioPath))) {
      return res.status(500).json({
        error: 'Cached audio file not found',
        message: '캐시된 음성 파일을 찾을 수 없습니다.'
      });
    }
    
    return res.json({
      success: true,
      audioPath: cachedData.audioPath,
      pythonOutput: cachedData.pythonOutput
    });
  }

  console.log(`Selected year: ${year}, semester: ${semester}, username: ${username}`);

  // 고유한 파일명 생성
  const timestamp = Date.now();
  const audioFileName = `grade_voice_${year}_${semester}_${timestamp}.mp3`;
  const outputPath = path.join(__dirname, 'public', audioFileName);
  const scriptPath = path.join(__dirname, '..', 'main.py');
  const pythonPath = 'python3';

  execFile(pythonPath, [
    scriptPath,
    username,
    password,
    year,
    semester,
    outputPath
  ], (error, stdout, stderr) => {
    if (error) {
      console.error('Error executing Python script:', error);
      console.error('Error details:', stderr);
      return res.status(500).json({
        error: 'Python script execution failed',
        details: error.message,
        stderr: stderr,
        stdout: stdout
      });
    }
    
    console.log('Python script output:', stdout);
    
    if (!require('fs').existsSync(outputPath)) {
      console.error('Audio file was not created');
      return res.status(500).json({
        error: 'Audio file was not created',
        pythonOutput: stdout
      });
    }

    // 이전 음성 파일들 정리
    const publicDir = path.join(__dirname, 'public');
    const files = require('fs').readdirSync(publicDir);
    const oldAudioFiles = files.filter(f => 
      f.startsWith('grade_voice_') && 
      f.endsWith('.mp3') && 
      f !== audioFileName
    );

// 1분 이상 된 파일들 삭제
const oneMinuteAgo = Date.now() - (60 * 1000);
oldAudioFiles.forEach(file => {
  const filePath = path.join(publicDir, file);
  const stats = require('fs').statSync(filePath);
  if (stats.mtimeMs < oneMinuteAgo) {
    try {
      require('fs').unlinkSync(filePath);
      console.log('Deleted old audio file:', file);
    } catch (err) {
      console.error('Error deleting file:', err);
    }
  }
});

    // 성적 데이터를 세션에 저장
    if (!req.session.gradeData) {
      req.session.gradeData = {};
    }
    req.session.gradeData[cacheKey] = {
      audioPath: '/' + audioFileName,
      pythonOutput: stdout
    };

    res.json({ 
      success: true,
      audioPath: '/' + audioFileName,
      pythonOutput: stdout 
    });
  });
});

// 서버 시작
const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});

// 주기적으로 오래된 음성 파일 삭제 (1분마다 체크)
setInterval(() => {
  const publicDir = path.join(__dirname, 'public');
  const files = require('fs').readdirSync(publicDir);
  const audioFiles = files.filter(f => f.startsWith('grade_voice_') && f.endsWith('.mp3'));
  const oneMinuteAgo = Date.now() - (60 * 1000);

  audioFiles.forEach(file => {
    const filePath = path.join(publicDir, file);
    const stats = require('fs').statSync(filePath);
    if (stats.mtimeMs < oneMinuteAgo) {
      try {
        require('fs').unlinkSync(filePath);
        console.log('Deleted old audio file:', file);
      } catch (err) {
        console.error('Error deleting file:', err);
      }
    }
  });
}, 60 * 1000);  // 1분마다 실행
