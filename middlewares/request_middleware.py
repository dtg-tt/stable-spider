from typing import Optional, Union

from fake_useragent import UserAgent

from core.request import StableRequest
from core.response import StableResponse


class RequestMiddleware:
    def __init__(self, spider: 'Spider'):
        self.spider = spider

    @staticmethod
    def get_ua():
        return UserAgent().random

    @staticmethod
    def cookie_list_to_cookie_str(cookies: list) -> str:
        """
        Converts cookies like:
        [{"domain": ".bloomberg.com", "httpOnly": false, "name": "_px2", "path": "/", "value": "eyJ1"}]

        into a string like:
        "_px2=eyJ1;"
        """
        cookie_list = []
        for cookie in cookies:
            cookie_str = f"{cookie.get('name')}={cookie.get('value')};"
            cookie_list.append(cookie_str)

        return " ".join(cookie_list)

    async def request_filter(self, request: 'StableRequest') -> bool:
        """
        Perform basic duplicate request filtering using fundamental data such as URL, data, json, and params.

        Args:
            request: The request.

        Returns:
            True if the request passes the filter.
            False if the request fails the filter.
        """
        self.spider.logger.info("request filter")
        return True

    async def process_request(
            self,
            request: 'StableRequest'
    ) -> Optional[Union['StableRequest', None]]:
        """
        Process the request before it is sent.

        Args:
            request: The request to be sent.

        Returns:
            The request to be sent, or
            None to discard the request.
        """
        self.spider.logger.info("process request")

        # Basic filtering
        if request.need_request_filter:
            # Perform basic URL filtering
            filter_res = await self.request_filter(request)
            # If the filter does not pass, return None
            if not filter_res:
                return None

    async def process_response(
            self,
            request: 'StableRequest',
            response: 'StableResponse'
    ) -> Optional[Union['StableRequest', 'StableResponse', None]]:
        """
        Process the response after the request has been sent.

        Args:
            request: The sent request.
            response: The received response.

        Returns:
            The request to resend, or
            The response to proceed to the next step, or
            None to discard the response.
        """
        self.spider.logger.info("process response")
        return response
