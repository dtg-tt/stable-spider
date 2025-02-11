from __future__ import annotations
import logging
import random
import time
from typing import AsyncGenerator, List, Literal, Optional

from selenium.webdriver import DesiredCapabilities, ActionChains
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from core.response import StableResponse
from log import create_logger
from core.request import StableRequest
from middlewares.item_middleware import ItemMiddleware
from middlewares.request_middleware import RequestMiddleware
from utils.selenium_driver import SeleniumDriver


class Spider:
    SPIDER_NAME = "Spider"  # Spider name

    REQUEST_MIDDLEWARES: List['RequestMiddleware'] = []  # Request middlewares
    ITEM_MIDDLEWARES: List['ItemMiddleware'] = []  # Item middlewares

    DEFAULT_REQUEST_MIDDLEWARES: List['RequestMiddleware'] = []  # Default request middlewares
    DEFAULT_ITEM_MIDDLEWARES: List['ItemMiddleware'] = []  # Default item middlewares

    START_URL_LIST = []  # Starting request URLs

    def __init__(self, need_default_request_middleware=True, need_default_item_middleware=True):
        """
            You need to implement start_spider() yourself, and it must be a generator.

            async def start_spider(self):
                yield StableRequest(url="https://www.baidu.com/", method='get')
        """
        # Ensure that data is not shared between different spider instances
        self.request_middlewares: List[RequestMiddleware] = []
        self.item_middlewares: List[ItemMiddleware] = []
        self.request_middlewares.extend(self.REQUEST_MIDDLEWARES.copy())
        self.item_middlewares.extend(self.ITEM_MIDDLEWARES.copy())
        self.spider_name = self.SPIDER_NAME
        self.start_url_list = self.START_URL_LIST.copy()

        if need_default_request_middleware:
            self.request_middlewares.extend(self.DEFAULT_REQUEST_MIDDLEWARES.copy())
        if need_default_item_middleware:
            self.item_middlewares.extend(self.DEFAULT_ITEM_MIDDLEWARES.copy())
        self.logger: logging.Logger = create_logger(self.SPIDER_NAME)

    # Spider start
    async def spider_start(self):
        self.logger.info(f"request middlewares: {self.request_middlewares}")
        self.logger.info(f"item middlewares: {self.item_middlewares}")
        self.logger.info(f"start url list: {self.start_url_list}")

        self.logger.info(f"spider_name: {self.spider_name} start")
        async for request in self.start_request():
            yield request

    # Start requests
    async def start_request(self):
        for start_url in self.start_url_list:
            yield StableRequest(url=start_url, method='GET', callback=self.parse, need_request_filter=False)

    async def spider_end(self):
        pass


class SeleniumSpider(Spider):
    SPIDER_NAME = "Spider"  # Spider name

    def __init__(
            self,
            options: Optional[webdriver.ChromeOptions] = None,
            service: Optional[Service] = None,
            keep_alive: bool = True,
            browser: Literal['chrome', 'firefox'] = 'chrome',
            grid_hub_url: str = None,
            need_default_options: bool = True,
            timeout: int = 20,
            debug: bool = False,
            selenium_driver=SeleniumDriver,
            need_default_request_middleware=True,
            need_default_item_middleware=True
    ):
        super().__init__(
            need_default_request_middleware=need_default_request_middleware,
            need_default_item_middleware=need_default_item_middleware
        )
        self.timeout = timeout
        self.options = options
        self.service = service
        self.keep_alive = keep_alive
        self.browser = browser
        self.need_default_options = need_default_options
        self.grid_hub_url = grid_hub_url
        self.debug = debug
        self.driver = selenium_driver(
            options=self.options,
            service=self.service,
            keep_alive=self.keep_alive,
            browser=self.browser,
            grid_hub_url=self.grid_hub_url,
            need_default_options=self.need_default_options,
            timeout=self.timeout,
            debug=self.debug,
        )

    def __del__(self):
        self.driver.quit()

    async def spider_end(self):
        self.driver.quit()
