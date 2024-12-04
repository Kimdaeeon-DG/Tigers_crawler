from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

def craw(id, passwd, year, semester):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('window-size=5000, 5000')
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(5000, 5000)


    URL = "https://sso.daegu.ac.kr/dgusso/ext/tigersstd/login_form.do?Return_Url=https://tigersstd.daegu.ac.kr/nxrun/ssoLogin.jsp"
    driver.get(URL)
    print("로그인 시작")

    driver.find_element(By.XPATH, '//*[@id="usr_id"]').click()
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="usr_id"]')))
    
    driver.find_element(By.XPATH, '//*[@id="usr_id"]').send_keys(id)
    driver.find_element(By.XPATH, '//*[@id="usr_pw"]').click()
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="usr_pw"]')))
    
    driver.find_element(By.XPATH, '//*[@id="usr_pw"]').send_keys(passwd)
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="idLoginForm"]/div[1]/div[3]/button')))
    
    driver.find_element(By.XPATH, '//*[@id="idLoginForm"]/div[1]/div[3]/button').click()
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="Mainframe.VFrameSet.TopFrame.form.mnTop.item1:text"]')))
    
    driver.find_element(By.XPATH, '//*[@id="Mainframe.VFrameSet.TopFrame.form.mnTop.item1:text"]').click()
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="Mainframe.VFrameSet.HFrameSet.LeftFrame.form.tabMenu.tabMnu.form.grdMnLeft.body.gridrow_2.cell_2_0.celltreeitem.treeitemtext:text"]')))


    driver.find_element(By.XPATH, '//*[@id="Mainframe.VFrameSet.HFrameSet.LeftFrame.form.tabMenu.tabMnu.form.grdMnLeft.body.gridrow_2.cell_2_0.celltreeitem.treeitemtext:text"]').click()
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="Mainframe.VFrameSet.HFrameSet.innerVFrameSet.innerHFrameSet.innerVFrameSet2.WorkFrame.0001300.form.rdHakjum.radioitem1:icontext"]/img')))

    driver.find_element(By.XPATH, '//*[@id="Mainframe.VFrameSet.HFrameSet.innerVFrameSet.innerHFrameSet.innerVFrameSet2.WorkFrame.0001300.form.rdHakjum.radioitem1:icontext"]/img').click()  
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
        answer = filter_strings(answer,selection)
        title = ""
        mystr = ""
        for item in answer:
            #'2023년도 2학기 빅컨셉+ 90 A'로 되어있기에 분리함.
            contents = item.split(" ")
            if (len(title) <= 0):
                title = contents[0] +" " + contents[1] + "의 성적을 안내드리겠습니다." 
            
            subject = contents[2] #과목
            point = contents[3] #점수
            grade = contents[4] #등급
            if point == "10":
                mystr += subject + last_string_check(subject) + " " + "패스등급을 받았습니다"
            else :
                mystr += subject + last_string_check(subject) + " " + point + "점을 맞았고" + grade + "의 등급을 받았습니다."
        new_answer = title + mystr 

    print("크롤링 종료")
    return new_answer

def filter_strings(arr,selection):
    return [s for s in arr if f"{selection}" in s]


def last_string_check(word):    #아스키(ASCII) 코드 공식에 따라 입력된 단어의 마지막 글자 받침 유무를 판단해서 뒤에 붙는 조사를 리턴하는 함수
    last = word[-1]
    criteria = (ord(last) - 44032) % 28
    if criteria == 0:       #나머지가 0이면 받침이 없는 것
        return '는'
    else:                   #나머지가 0이 아니면 받침 있는 것
        return '은'