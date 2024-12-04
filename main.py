import Tools.crawler
from tts import TTS
import argparse
import sys

def verify_login(username, password):
    try:
        # 로그인 검증만 수행
        Tools.crawler.verify_login(username, password)
        return True
    except Exception as e:
        print(str(e), file=sys.stderr)
        return False

def create_audio_from_text(text, output_path):
    try:
        tts = TTS()
        tts.save_sound(text, output_path)
        return True
    except Exception as e:
        print(str(e), file=sys.stderr)
        return False

def main(username, password, year=None, semester=None, output_path=None, cached_text=None):
    try:
        if cached_text:
            # 캐시된 텍스트로 음성 파일 생성
            if not create_audio_from_text(cached_text, output_path):
                sys.exit(1)
        elif year and semester:
            # 성적 데이터 크롤링
            tts = TTS()
            sentence = Tools.crawler.craw(username, password, year, semester)
            print(sentence)
            if output_path:
                tts.save_sound(sentence, output_path)
        else:
            # 로그인 검증만 수행
            if not verify_login(username, password):
                sys.exit(1)
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="대구대학교 성적 크롤러")
    parser.add_argument('--verify-login', action='store_true', help='로그인 검증만 수행')
    parser.add_argument('--cached-text', action='store_true', help='캐시된 텍스트로 음성 파일 생성')
    parser.add_argument('username', type=str, help='아이디')
    parser.add_argument('password', type=str, help='비밀번호')
    parser.add_argument('year', type=str, nargs='?', help='년도')
    parser.add_argument('semester', type=str, nargs='?', help='학기')
    parser.add_argument('output_path', type=str, nargs='?', help='출력 경로')
    parser.add_argument('text', type=str, nargs='?', help='캐시된 텍스트')
    args = parser.parse_args()
    
    if args.verify_login:
        main(args.username, args.password)
    elif args.cached_text:
        main(args.username, args.password, args.year, args.semester, args.output_path, args.text)
    else:
        main(args.username, args.password, args.year, args.semester, args.output_path)
