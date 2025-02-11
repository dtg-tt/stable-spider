import os
import random
import time
from typing import Optional, Literal

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from undetected_chromedriver.options import ChromeOptions

from core.response import StableResponse
from utils.retry import retry

GRID_HUB_URL = os.getenv('GRID_HUB_URL', None)


class SeleniumDriver:
    def __init__(
            self,
            options: Optional[webdriver.ChromeOptions | ChromeOptions] = None,
            service: Optional[Service] = None,
            keep_alive: bool = True,
            browser: Literal['chrome', 'firefox'] = 'chrome',
            grid_hub_url: str = GRID_HUB_URL,
            need_default_options: bool = True,
            timeout: int = 20,
            debug: bool = False
    ):
        self.need_default_options = need_default_options
        self.timeout = timeout
        self.options = options
        self.service = service
        self.keep_alive = keep_alive
        self.browser = browser
        if grid_hub_url:
            self.grid_hub_url = grid_hub_url
        else:
            self.grid_hub_url = GRID_HUB_URL
        self.debug = debug
        self.start_browser()

    def start_browser(self):
        # 如果没有传入options
        if not self.options:
            self.options = webdriver.ChromeOptions()

        # if not self.debug:
        #     self.options.add_argument('--headless')  # 设置无头模式

        # 设置默认配置
        if self.need_default_options:
            self.options.add_argument('--no-sandbox')  # 防止linux报错
            self.options.add_experimental_option('excludeSwitches', ['enable-automation'])  # 防检测
            self.options.add_experimental_option('useAutomationExtension', False)  # 防检测
            self.options.add_argument('--disable-blink-features=AutomationControlled')
            self.options.add_argument('--disable-gpu')  # 禁用GPU加速
            self.options.add_argument('--window-size=1920x1080')  # 设置窗口大小

            if not self.debug:
                self.options.add_argument("--disable-dev-shm-usage")  # 防止grid报错

        if not self.debug:
            self.driver = webdriver.Remote(
                command_executor=self.grid_hub_url,
                options=self.options,
                keep_alive=self.keep_alive
            )
        else:
            self.driver = webdriver.Chrome(
                options=self.options,
                service=self.service,
                keep_alive=self.keep_alive
            )

        self.driver.implicitly_wait(self.timeout)  # 全局自动等待元素加载，不要混合使用隐式、显式等待
        self.driver.maximize_window()  # 全屏打开
        self.action = ActionChains(self.driver)

    def __call__(self, *args, **kwargs):
        return self.driver

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("driver异常")
        self.quit()

    @retry()
    def get(self, url):
        self.driver.get(url)
        html = self.get_html()
        selector = StableResponse.parser_html(html)
        return selector

    @retry()
    def switch_to_frame(self, iframe):
        """进入iframe"""
        self.driver.switch_to.frame(iframe)

    @retry()
    def switch_to_default_content(self):
        """回到默认内容"""
        self.driver.switch_to.default_content()

    @retry()
    def click(self, value=None, by=By.XPATH):
        button = self.driver.find_element(by, value)
        button.click()

    @retry()
    def click_element(self, element):
        self.action.move_to_element(element).click().perform()

    @retry()
    def find_element(self, value=None, by=By.XPATH, need_retry=True, not_find_raise=True):
        try:
            return self.driver.find_element(by, value)
        except NoSuchElementException as e:
            if not_find_raise:
                raise e
            else:
                return False

    @retry()
    def find_elements(self, value=None, by=By.XPATH, need_retry=True):
        return self.driver.find_elements(by, value)

    @retry()
    def send_key(self, value=None, key='', by=By.XPATH):
        button = self.driver.find_element(by, value)
        button.send_keys(key)

    @retry()
    def get_cookies(self):
        return self.driver.get_cookies()

    @retry()
    def get_cookie(self, name):
        return self.driver.get_cookie(name)

    def add_cookies(self, cookies):
        for cookie in cookies:
            self.driver.add_cookie(cookie)

    @retry()
    def delete_cookie(self, name):
        return self.driver.delete_cookie(name)

    @retry()
    def delete_cookies(self, names):
        for name in names:
            self.driver.delete_cookie(name)

    @retry()
    def delete_all_cookies(self):
        self.driver.delete_all_cookies()

    @retry()
    def refresh(self):
        self.driver.refresh()

    @retry()
    def back(self):
        self.driver.back()

    @retry()
    def scroll_to_element(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView();", element)

    @retry()
    def get_html(self):
        return self.driver.page_source

    @retry()
    def get_png(self, file_name):
        self.driver.save_screenshot(f"{file_name}.png")

    def execute_script(self, script):
        return self.driver.execute_script(script=script)

    def sleep(self, s_time=1, e_time=None):
        if not e_time:
            e_time = s_time + 2
        time.sleep(random.randint(s_time, e_time))

    def get_driver(self):
        return self.driver

    def quit(self):
        print("driver结束")
        if hasattr(self, 'driver') and self.driver:
            self.driver.quit()
            self.driver = None


if __name__ == '__main__':
    options = ChromeOptions()
    driver = SeleniumDriver()
    driver.get("https://www.baidu.com")
    r = (driver.find_element('//*[@id="s_lg_img"]')).get_attribute('src')
    print(r)
