from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

import time

def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    try:
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(10)  # 암시적 대기 추가
        return driver
    except Exception as e:
        print(f"Error creating Chrome driver: {str(e)}")
        raise e

def verify_login(id, passwd):
    driver = get_driver()
    print("Starting login verification...")

    try:
        URL = "https://sso.daegu.ac.kr/dgusso/ext/tigersstd/login_form.do?Return_Url=https://tigersstd.daegu.ac.kr/nxrun/ssoLogin.jsp"
        print(f"Navigating to URL: {URL}")
        driver.get(URL)
        
        print("Waiting for login form...")
        time.sleep(3)  

        print("Finding login elements...")
        id_input = driver.find_element(By.ID, 'id')
        pw_input = driver.find_element(By.ID, 'passwd')
        
        print(f"Entering credentials for ID: {id}")
        id_input.send_keys(id)
        pw_input.send_keys(passwd)
        
        print("Clicking login button...")
        driver.find_element(By.CLASS_NAME, 'btn_login').click()
        
        print("Waiting for login process...")
        time.sleep(5)  
        
        print("Current URL:", driver.current_url)
        
        # 로그인 실패 확인
        error_elements = driver.find_elements(By.CLASS_NAME, 'error')
        if error_elements:
            error_text = error_elements[0].text
            print(f"Login error detected: {error_text}")
            raise Exception(error_text or "로그인에 실패했습니다.")
            
        print("Login successful!")
        return True
        
    except Exception as e:
        print(f"Login verification failed: {str(e)}")
        raise e
    
    finally:
        print("Closing browser...")
        driver.quit()

def craw(id, passwd, year, semester):
    driver = get_driver()
    print(f"Starting grade crawling for {id}, year: {year}, semester: {semester}")

    try:
        URL = "https://sso.daegu.ac.kr/dgusso/ext/tigersstd/login_form.do?Return_Url=https://tigersstd.daegu.ac.kr/nxrun/ssoLogin.jsp"
        print(f"Navigating to URL: {URL}")
        driver.get(URL)
        
        print("Waiting for login form...")
        time.sleep(3)

        print("Finding login elements...")
        id_input = driver.find_element(By.ID, 'id')
        pw_input = driver.find_element(By.ID, 'passwd')
        
        print(f"Entering credentials for ID: {id}")
        id_input.send_keys(id)
        pw_input.send_keys(passwd)
        
        print("Clicking login button...")
        driver.find_element(By.CLASS_NAME, 'btn_login').click()
        
        print("Waiting for login process...")
        time.sleep(5)

        print("Current URL after login:", driver.current_url)
        
        # 로그인 실패 확인
        error_elements = driver.find_elements(By.CLASS_NAME, 'error')
        if error_elements:
            error_text = error_elements[0].text
            print(f"Login error detected: {error_text}")
            raise Exception(error_text or "로그인에 실패했습니다.")
            
        print("로그인 종료")

        answer = []
        i = 0
        flag = True
        print("크롤링 시작")
        while flag:
            try:
                element = driver.find_element(By.XPATH, '//*[@id="Mainframe.VFrameSet.HFrameSet.innerVFrameSet.innerHFrameSet.innerVFrameSet2.WorkFrame.0001300.form.Tab01.tabpage1.form.Grid00.body.gridrow_' + str(i) + '"]')
                temp = element.get_attribute('aria-label')
                splited_string = temp.split(" ")
                if splited_string[2] == "균형" or splited_string[2] == "공통" or splited_string[2] == "자유":
                    grade = (splited_string[0] + "년도 " + splited_string[1] + "학기 " + splited_string[4] + " " + splited_string[6] + " " + splited_string[7])
                else:
                    grade = (splited_string[0] + "년도 " + splited_string[1] + "학기 " + splited_string[3] + " " + splited_string[5] + " " + splited_string[6])
                answer.append(grade)
                i = i + 1
            except NoSuchElementException:
                flag = False      
        if year == "all":
            return answer
        else:
            selection = str(year)+"년도 "+str(semester) + "학기"
            answer = filter_strings(answer, selection)
            title = ""
            mystr = ""
            for item in answer:
                contents = item.split(" ")
                if (len(title) <= 0):
                    title = contents[0] +" " + contents[1] + "의 성적을 안내드리겠습니다." 
            
                subject = contents[2] #과목
                point = contents[3] #점수
                grade = contents[4] #등급
                if point == "10":
                    mystr += subject + last_string_check(subject) + " " + "패스등급을 받았습니다"
                else:
                    mystr += subject + last_string_check(subject) + " " + point + "점을 맞았고" + grade + "의 등급을 받았습니다."
            new_answer = title + mystr 

        print("크롤링 종료")
        return new_answer

    except Exception as e:
        print(f"Crawling failed: {str(e)}")
        raise e

    finally:
        print("Closing browser...")
        driver.quit()

def filter_strings(arr, selection):
    return [s for s in arr if f"{selection}" in s]

def last_string_check(word):
    if not word:
        return ""
    last = word[-1]
    if '가' <= last <= '힣':
        if (ord(last) - ord('가')) % 28 > 0:
            return '은'
    return '는'