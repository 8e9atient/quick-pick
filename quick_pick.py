import re

from tabulate import tabulate

import environ
from selenium.webdriver.support import expected_conditions as EC

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

# tabulate headers
li = []
headers = [
    "Purchase Date",
    "Lottery Name",
    "Round",
    "Selected Numbers/Lottery Numbers",
    "Number of Purchases",
    "Winning Result",
    "Rank",
    "Draw Date"
]
li.append(headers)

# .env
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(env_file='./.env')

# 웹 드라이버 옵션 설정
options = Options()
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("detach", True)

# 웹 드라이버 초기화 (Selenium 4 이상)
s = Service('./chromedriver.exe')
driver = webdriver.Chrome(service=s, options=options)

# 1. 로그인 페이지 이동
driver.get("https://dhlottery.co.kr/common.do?method=main")

login_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, 'body > div:nth-child(1) > header > div.header_con > div.top_menu > form > div > ul > li.log > a'))
).send_keys('\n')

# 2. 로그인
id_field = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.ID, 'userId'))
).send_keys(env('USERNAME'))
driver.find_element(By.NAME, 'password').send_keys(env('PASSWORD'))
driver.find_element(By.XPATH, '//*[@id="article"]/div[2]/div/form/div/div[1]/fieldset/div[1]/a').click()

# 3. 예치금 확인
money = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.CSS_SELECTOR, 'body > div:nth-child(1) > header > div.header_con > div.top_menu > form > div > ul.information > li.money > a:nth-child(2) > strong'))
).text

if int(''.join(re.findall('\d+', money))) < 1000:
    print(f"잔액이 부족합니다.")
else:
    # 4. 자동번호 선택 후 구매
    driver.get('https://el.dhlottery.co.kr/game/TotalGame.jsp?LottoId=LO40')

    iframe = driver.find_element(By.ID, 'ifrm_tab')
    driver.switch_to.frame(iframe)

    auto_number_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'num2'))
    ).send_keys('\n')
    driver.find_element(By.XPATH, '//*[@id="btnSelectNum"]').click()
    driver.find_element(By.XPATH, '//*[@id="btnBuy"]').click()
    driver.find_element(By.XPATH, '//*[@id="popupLayerConfirm"]/div/div[2]/input[1]').click()
    driver.find_element(By.XPATH, '//*[@id="closeLayer"]').click()

    driver.switch_to.default_content()

    # 5. 당첨여부 확인
    driver.get("https://dhlottery.co.kr/myPage.do?method=lottoBuyListView")

    week = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, '#frm > table > tbody > tr:nth-child(3) > td > span.period > a:nth-child(2)'))
    ).send_keys('\n')
    driver.find_element(By.XPATH, '//*[@id="submit_btn"]').click()

    result_iframe = driver.find_element(By.ID, 'lottoBuyList')
    driver.switch_to.frame(result_iframe)

    result_table = driver.find_element(By.CSS_SELECTOR, 'body > table')
    result_table_tr = result_table.find_elements(By.TAG_NAME, 'tr')

    for i in range(1, len(result_table_tr)):
        li.append([j.text for j in result_table_tr[i].find_elements(By.TAG_NAME, 'td')])

    res = tabulate(li, tablefmt='grid')
    driver.switch_to.default_content()

    money = driver.find_element(By.CSS_SELECTOR, 'body > div:nth-child(1) > header > div.header_con > div.top_menu > form > div > ul.information > li.money > a:nth-child(2) > strong').text

    print(res)
    print(f"현재 예치금 잔액: {money}")

# 6. 웹 드라이버 종료
driver.quit()
