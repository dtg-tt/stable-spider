import random
import asyncio
from typing import Callable, Optional, Dict, List, Literal

import httpx

from core.response import StableResponse
from utils.retry import async_retry


class BaseRequest:
    def __init__(
            self,
            url: str,
            method: Literal['GET', 'POST'] = 'GET',
            callback: Optional[Callable] = None,
            data=None,
            json=None,
            params=None,
            cookies=None,
            headers: Optional[Dict] = None,
            meta: Optional[Dict] = None,
            need_request_filter: bool = True,
            need_response_filter: bool = True,
            timeout: int = 10,
            request_interval_time: int = 3,
            request_interval_time_random_range: int = 5
    ):
        """
        Common initialization parameters:
            url: request URL
            method: request method (GET or POST)
            callback: callback function after the request is completed
            data/json/params/cookies/headers: request data related parameters
            meta: used to pass custom data
            need_request_filter/need_response_filter: whether filtering is needed
            timeout: request timeout duration
            request_interval_time: base time interval between requests
            request_interval_time_random_range: additional random range for the request interval
        """
        self.url = url
        self.method = method
        self.callback = callback
        self.data = data
        self.json = json
        self.params = params
        self.cookies = cookies
        self.headers = headers if headers is not None else {}
        self.meta = meta if meta is not None else {}
        self.need_request_filter = need_request_filter
        self.need_response_filter = need_response_filter
        self.timeout = timeout
        self.request_interval_time = request_interval_time
        self.request_interval_time_random_range = request_interval_time_random_range

    async def random_sleep(self):
        delay = random.randint(
            self.request_interval_time,
            self.request_interval_time + self.request_interval_time_random_range
        )
        await asyncio.sleep(delay)

    async def fetch(self) -> StableResponse:
        """Abstract method, implement the specific request logic in subclasses."""
        raise NotImplementedError("Subclasses must implement fetch method")


class StableRequest(BaseRequest):
    @async_retry()
    async def fetch(self) -> StableResponse:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            # Control the request rate
            await self.random_sleep()
            response = await client.request(
                method=self.method,
                url=self.url,
                params=self.params,
                data=self.data,
                json=self.json,
                headers=self.headers,
                cookies=self.cookies
            )
        return StableResponse(response=response, request=self)


class StableSeleniumRequest(BaseRequest):
    def __init__(
            self,
            url: str,
            driver,
            method: Literal['GET'] = 'GET',
            callback: Optional[Callable] = None,
            data=None,
            json=None,
            params=None,
            cookies=None,
            headers: Optional[Dict] = None,
            meta: Optional[Dict] = None,
            need_request_filter: bool = True,
            need_response_filter: bool = True,
            timeout: int = 10,
            request_interval_time: int = 3,
            request_interval_time_random_range: int = 5
    ):
        super().__init__(
            url=url,
            method=method,
            callback=callback,
            data=data,
            json=json,
            params=params,
            cookies=cookies,
            headers=headers,
            meta=meta,
            need_request_filter=need_request_filter,
            need_response_filter=need_response_filter,
            timeout=timeout,
            request_interval_time=request_interval_time,
            request_interval_time_random_range=request_interval_time_random_range
        )
        self.driver = driver

    async def fetch(self) -> StableResponse:
        # Control the request rate
        await self.random_sleep()
        selector = self.driver.get(self.url)
        return StableResponse(selector=selector, request=self)
