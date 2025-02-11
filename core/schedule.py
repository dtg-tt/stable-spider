import asyncio
import inspect
from typing import Optional, Union, AsyncGenerator, List

from core.item import StableItem
from core.request import BaseRequest
from core.response import StableResponse
from core.spider import Spider


class Schedule:
    def __init__(self, spider: 'Spider', request_middleware_instances: List):
        self.spider = spider
        self.request_middleware_instances = request_middleware_instances

    async def schedule(
            self,
            yield_res: Optional[Union[BaseRequest, StableResponse, StableItem]]
    ) -> AsyncGenerator:
        """
        Scheduling entry point:
          - If the input is a request (an instance of BaseRequest), perform the full scheduling process.
          - Otherwise, directly yield return it (e.g., an Item or final result).
        """
        if isinstance(yield_res, BaseRequest):
            async for result in self._process_request(yield_res):
                yield result
        else:
            yield yield_res

    async def _process_request(
            self, request: BaseRequest
    ) -> AsyncGenerator:
        spider = self.spider
        spider.logger.info(f"{spider.SPIDER_NAME} Scheduler processing request: {request.url}")

        # 1. Pre-request middleware processing
        processed_req = await self._run_request_middlewares(request)
        if processed_req is None:
            spider.logger.info(f"{spider.SPIDER_NAME} Request middleware intercepted request: {request.url}")
            return

        # 2. Initiate request
        response = await processed_req.fetch()
        spider.logger.info(f"{spider.SPIDER_NAME} Request completed: {request.url}")

        # 3. Response middleware processing
        processed_response = await self._run_response_middlewares(processed_req, response)
        if processed_response is None:
            spider.logger.info(f"{spider.SPIDER_NAME} Response middleware intercepted response: {request.url}")
            return
        elif isinstance(processed_response, BaseRequest):
            spider.logger.info(f"{spider.SPIDER_NAME} Response middleware returned a new request: {request.url}")
            async for res in self.schedule(processed_response):
                yield res
            return

        # 4. Invoke callback processing
        async for res in self._process_callback(processed_req, processed_response):
            yield res

    async def _run_request_middlewares(
            self, request: BaseRequest
    ) -> Optional[BaseRequest]:
        for middleware in self.request_middleware_instances:
            request = await middleware.process_request(request)
            if request is None:
                self.spider.logger.info(
                    f"{self.spider.SPIDER_NAME} Request middleware {middleware} intercepted the request")
                return None
        return request

    async def _run_response_middlewares(
            self,
            request: BaseRequest,
            response: StableResponse,
    ) -> Optional[Union[StableResponse, BaseRequest]]:
        for middleware in self.request_middleware_instances:
            response = await middleware.process_response(request=request, response=response)
            if response is None:
                self.spider.logger.info(
                    f"{self.spider.SPIDER_NAME} Response middleware {middleware} intercepted the response")
                return None
            elif isinstance(response, BaseRequest):
                self.spider.logger.info(
                    f"{self.spider.SPIDER_NAME} Response middleware {middleware} returned a new request")
                return response
        return response

    async def _process_callback(
            self,
            request: BaseRequest,
            response: StableResponse,
    ) -> AsyncGenerator:
        callback = request.callback
        self.spider.logger.info(f"{self.spider.SPIDER_NAME} Invoking callback function: {callback}")
        meta = request.meta

        if callback is None:
            yield response
        # If the callback is an async generator function, call it asynchronously
        elif inspect.isasyncgenfunction(callback):
            async for callback_res in callback(response=response, meta=meta):
                async for res in self.schedule(callback_res):
                    yield res
        elif asyncio.iscoroutinefunction(callback):
            callback_res = await callback(response=response, meta=meta)
            async for res in self.schedule(callback_res):
                yield res
        else:
            callback_res = callback(response=response, meta=meta)
            async for res in self.schedule(callback_res):
                yield res

    # async def schedule(self, yield_res: StableRequest = None):
    #
    #     # 如果是请求那么发送请求,寻找callback
    #     if isinstance(yield_res, BaseRequest):
    #         self.spider.logger.info(f"{self.spider.SPIDER_NAME} 调度器接受请求:{yield_res.url}")
    #
    #         request = yield_res
    #         # 发送请求前 执行请求中间件
    #         for request_middleware_instance in self.request_middleware_instances:
    #             # 调用中间件中处理请求方法
    #             request = await request_middleware_instance.process_request(request)
    #             # 如果返回为None则break,本次请求结束
    #             if request is None:
    #                 self.spider.logger.info(
    #                     f"{self.spider.SPIDER_NAME} 请求中间件 {request_middleware_instance} 未通过:{yield_res.url}"
    #                 )
    #                 # async for schedule_res in self.schedule(yield_res=None):
    #                 #     yield schedule_res
    #                 break
    #         else:
    #             # 中间件通过,发出请求
    #             response = await request.fetch()
    #             self.spider.logger.info(f"{self.spider.SPIDER_NAME} 请求中间件通过:{yield_res.url}")
    #
    #             # 发送请求后 执行请求中间件
    #             for request_middleware_instance in self.request_middleware_instances:
    #                 response = await request_middleware_instance.process_response(request=request, response=response)
    #
    #                 # 如果返回为None则break,本次请求结束
    #                 if response is None:
    #                     self.spider.logger.info(
    #                         f"{self.spider.SPIDER_NAME} 响应中间未件{request_middleware_instance} 未通过:{yield_res.url} 抛弃")
    #                     break
    #
    #                 # 如果是请求则返回到调度器重新执行
    #                 elif isinstance(response, StableRequest):
    #                     self.spider.logger.info(
    #                         f"{self.spider.SPIDER_NAME} 响应中间件{request_middleware_instance} 未通过:{yield_res.url} 重新请求")
    #                     async for schedule_res in self.schedule(yield_res=yield_res):
    #                         yield schedule_res
    #             else:
    #                 self.spider.logger.info(f"{self.spider.SPIDER_NAME} 响应中间件通过:{yield_res.url}")
    #
    #                 # 获取回调函数
    #                 callback = request.callback
    #                 self.spider.logger.info(f"{self.spider.SPIDER_NAME} 回调函数为:{callback}")
    #
    #                 # 获取meta
    #                 meta = request.meta
    #                 # 如果是生成器则 再次异步调用回调函数 调用即可无需返回
    #                 if inspect.isasyncgenfunction(callback):
    #                     async for callback_res in callback(response=response, meta=meta):
    #                         async for schedule_res in self.schedule(yield_res=callback_res):
    #                             yield schedule_res
    #                 elif asyncio.iscoroutinefunction(callback):
    #                     callback_res = await callback(response=response, meta=meta)
    #                     async for schedule_res in self.schedule(yield_res=callback_res):
    #                         yield schedule_res
    #     else:
    #         yield yield_res
