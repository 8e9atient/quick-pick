import configparser
import unittest

from selenium.webdriver.support import expected_conditions as EC

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


class QuickPickTest(unittest.TestCase):
    def setUp(self) -> None:
        # config.ini
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

        # 웹 드라이버
        options = Options()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("detach", True)

        s = Service('./chromedriver.exe')
        self.driver = webdriver.Chrome(service=s, options=options)

    def login(self):
        driver = self.driver
        driver.get("https://dhlottery.co.kr/common.do?method=main")

        # 로그인 버튼
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR,
                                        'body > div:nth-child(1) > header > div.header_con > div.top_menu > form > div > ul > li.log > a'))
        ).send_keys('\n')

        # username, password
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'userId'))
        ).send_keys(self.config['credentials']['username'])
        driver.find_element(By.NAME, 'password').send_keys(self.config['credentials']['password'])

        # 로그인 버튼
        driver.find_element(By.XPATH, '//*[@id="article"]/div[2]/div/form/div/div[1]/fieldset/div[1]/a').click()

    def test_login(self) -> None:
        self.login()

        # 로그아웃 버튼
        logout_btn = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'body > div:nth-child(1) > header > div.header_con > div.top_menu > form > div > ul.account > li.log.devide > a'))
        )

        # 로그아웃 버튼이 생기면 테스트 성공
        self.assertTrue(logout_btn.is_displayed(), "로그인 실패")

    def test_result(self) -> None:
        self.login()

        li = [[
            "Purchase Date",
            "Lottery Name",
            "Round",
            "Selected Numbers/Lottery Numbers",
            "Number of Purchases",
            "Winning Result",
            "Rank",
            "Draw Date"
        ]]

        driver = self.driver
        driver.get("https://dhlottery.co.kr/myPage.do?method=lottoBuyListView")

        # 구매 목록
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '#frm > table > tbody > tr:nth-child(3) > td > span.period > a:nth-child(2)'))
        ).send_keys('\n')
        driver.find_element(By.XPATH, '//*[@id="submit_btn"]').click()

        result_iframe = driver.find_element(By.ID, 'lottoBuyList')
        driver.switch_to.frame(result_iframe)

        result_table = driver.find_element(By.CSS_SELECTOR, 'body > table')
        message = result_table.find_elements(By.XPATH, "./tr/td[contains(text(), '조회 결과가 없습니다.')]")

        if message:
            # '조회 결과가 없습니다.' 메시지가 있으면 테스트 실패
            self.fail("조회 결과가 없습니다.")
        else:
            # '조회 결과가 없습니다.' 메시지가 없으면 테스트 성공 -> 구매한 내역이 있는 경우
            pass

        driver.switch_to.default_content()

    def tearDown(self):
        self.driver.quit()


if __name__ == '__main__':
    unittest.main()
