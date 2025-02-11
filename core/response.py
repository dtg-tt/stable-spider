from typing import List, Optional

from httpx import Response
from parsel import Selector


class StableResponse:
    def __init__(self, response: 'Response' = None, request=None, selector=None):
        self._response: Response = response
        self.request = request
        self.selector = selector

    @classmethod
    def parser_html(cls, html):
        """Generate a Selector object from the provided HTML."""
        selector = Selector(text=html)
        return selector

    def parser_response(self) -> Selector:
        """Parse the response content using lxml if an underlying response exists."""
        if not self._response:
            raise ValueError("No response to parse")
        return Selector(text=self._response.text)

    def xpath(self, xpath_query: str):
        """Unified XPath query interface."""
        sel = self.selector if self.selector is not None else self.parser_response()
        return sel.xpath(xpath_query)

    @property
    def status_code(self) -> int:
        """Provide access to the status code; raises an exception if there is no underlying response."""
        if self._response is not None:
            return self._response.status_code
        raise AttributeError("No underlying response available")

    @property
    def text(self) -> str:
        """Directly retrieve the response text."""
        if self._response is not None:
            return self._response.text
        raise AttributeError("No underlying response available")

    def json(self):
        """Parse the response as JSON."""
        if self._response is not None:
            return self._response.json()
        raise AttributeError("No underlying response available")

    def __getattr__(self, item):
        if not self._response:
            return self.__getattribute__(item)

        try:
            _response = self.__getattribute__("_response")
            return getattr(_response, item)
        except AttributeError:
            return self.__getattribute__(item)
