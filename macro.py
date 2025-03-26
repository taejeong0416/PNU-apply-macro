from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
import urllib.request
import time

URL = 'https://sugang.pusan.ac.kr/main'
TIME_FORMAT = '%Y. %m. %d %H:%M:%S'
START_TIME = '2025. 02. 12 08:00:00'  # 수강신청 시작 시간
LOGIN_OFFSET = 40  # 몇 초 전에 로그인 시도할지


def initialize_browser():
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(10)
    return driver


def parse_time_to_seconds(timestr, fmt, server=False):
    dt = datetime.strptime(timestr, fmt)
    if server:
        dt += timedelta(hours=9)
    return dt.timestamp()


def fetch_server_time():
    response = urllib.request.urlopen(URL)
    server_time_raw = response.headers['Date']
    trimmed = server_time_raw.rstrip(' GMT')[5:]
    server_sec = parse_time_to_seconds(trimmed, '%d %b %Y %H:%M:%S', server=True)
    response.close()
    return server_sec


def perform_login(driver, login_deadline):
    while True:
        current = fetch_server_time()
        if current >= login_deadline:
            driver.get(URL)
            driver.find_element(By.ID, "userID").send_keys("ID")
            driver.find_element(By.ID, "userPW").send_keys("PWD")
            driver.find_element(By.ID, "btnLogin").click()
            print("[로그인] 로그인 완료.")
            break
        time.sleep(1)


def close_alert_if_exists(driver, wait):
    try:
        alert_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="root"]/div[2]/div[2]/p/a')
        ))
        alert_btn.click()
        print("[알림] 팝업 닫힘")
    except Exception:
        pass


def countdown_to_start(driver, target_ts, wait):
    while True:
        clock_str = driver.find_element(By.ID, "clock").text
        now_ts = parse_time_to_seconds(clock_str, TIME_FORMAT)
        remaining = target_ts - now_ts
        print(f"[대기] 서버 시계: {clock_str} | 남은 시간: {remaining:.2f}초")
        if remaining <= 1:
            print("[시작] 수강신청 시작")
            time.sleep(0.6)
            break
        time.sleep(0.1)


def apply_for_courses(driver, wait):
    driver.find_element(By.ID, "lecapplyShortCutBtn").click()
    apply_selector = '.btn.btn-outline-primary.basket-apply'

    while True:
        try:
            buttons = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, apply_selector))
            )

            for _ in range(len(buttons)):
                btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, apply_selector)))
                btn.click()
                wait.until(EC.staleness_of(btn))

        except TimeoutException:
            print("[완료] 수강신청 종료")
            break


def main():
    driver = initialize_browser()
    wait = WebDriverWait(driver, 25)
    target_time = parse_time_to_seconds(START_TIME, TIME_FORMAT)
    login_time = target_time - LOGIN_OFFSET

    perform_login(driver, login_time)
    close_alert_if_exists(driver, wait)
    countdown_to_start(driver, target_time, wait)
    apply_for_courses(driver, wait)


if __name__ == "__main__":
    main()
