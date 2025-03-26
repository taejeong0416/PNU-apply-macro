from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
import time
import urllib.request
from datetime import datetime
from datetime import timedelta

# Chrome 옵션 설정
webdriver_options = webdriver.ChromeOptions()
webdriver_options.add_experimental_option("detach", True)  # 창을 닫지 않도록 설정

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=webdriver_options)
driver.implicitly_wait(10)
wait = WebDriverWait(driver, 25)
url = 'https://sugang.pusan.ac.kr/main'

# 수강신청 날짜 설정
time_format = '%Y. %m. %d %H:%M:%S'
apply_day_str = '2025. 02. 12 08:00:00'  # 수강신청 시작 시간 설정

# 초단위 시간 반환 함수
def get_sec(time_str, time_format, is_server):
    sec = datetime.strptime(time_str, time_format)
    if is_server == 1:
        sec += timedelta(hours=9)
    return float(sec.timestamp())

target_sec = get_sec(apply_day_str, time_format, 0)

# 서버 시간 가져오기
def get_server_time():
    response = urllib.request.urlopen(url)
    date_str = response.headers['Date']
    date_str = date_str.rstrip(' GMT')[5:]
    server_sec = get_sec(date_str, '%d %b %Y %H:%M:%S', 1)
    response.close()
    return server_sec

# 40초 전에 로그인 준비
login_time = target_sec - 40
while True:
    login_sec = get_server_time()

    # URL로 접속
    driver.get(url)
    print(f"현재 서버 시간: {login_sec}, 목표 시간: {login_time}")

    if login_time <= login_sec:
        driver.find_element(By.ID, "userID").send_keys("ID")   # 아이디 삽입
        driver.find_element(By.ID, "userPW").send_keys("PWD") # 비밀번호 삽입
        driver.find_element(By.ID, "btnLogin").click()
        break
    else:
        time.sleep(1)  # 1초 간격으로 서버 시간 체크

# 알림창 처리 함수
def handle_alert():
    try:
        alert_xpath = '//*[@id="root"]/div[2]/div[2]/p/a'
        alert_btn = wait.until(EC.element_to_be_clickable((By.XPATH, alert_xpath)))
        alert_btn.click()
        return True
    except TimeoutException:
        return False
    except Exception:
        return False

handle_alert()

# 수강 신청 카운트다운
while True:
    clock_str = driver.find_element(By.ID, "clock").text
    timing_sec = get_sec(clock_str, time_format, 0)
    milli_diff = target_sec - timing_sec

    print(f"현재 시계: {clock_str}, 남은 시간: {milli_diff:.2f}초")
    if milli_diff <= 1:
        print("수강신청을 시작합니다!")
        time.sleep(0.6)
        break
    time.sleep(0.1)

# 수강신청 버튼 클릭
apply_btn_id = "lecapplyShortCutBtn"
driver.find_element(By.ID, apply_btn_id).click()

# 수강신청 작업 반복
sub_apply_btn = '.btn.btn-outline-primary.basket-apply'
while True:
    try:
        subjects = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, sub_apply_btn))
        )

        for _ in range(len(subjects)):
            element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, sub_apply_btn)))
            element.click()
            wait.until(EC.staleness_of(element))

    except TimeoutException:
        print("모든 수강신청 완료!")
        break
