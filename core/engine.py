import traceback

from core.item import StableItem
from core.schedule import Schedule
from core.spider import Spider


class Engine:

    def __init__(self, spider: 'Spider'):
        self.spider = spider
        self.spider_start = False

    async def start(self):
        spider = self.spider
        # Mark the signal as started
        self.spider_start = True
        self.spider.logger.info(f"Engine started, spider: {self.spider.spider_name}")

        # Initialize request and item middleware instances
        request_middleware_instances, item_middleware_instances = self._init_middlewares()

        # Pass the request to the scheduler
        schedule = Schedule(spider=spider, request_middleware_instances=request_middleware_instances)

        # Process the spider's startup requests
        async for request in spider.spider_start():
            spider.logger.info(f"{spider.spider_name} loop starting request for URL: {request.url}")

            # Check if exit is required
            if not self.spider_start:
                break

            try:
                await self._handle_request_pipeline(request, schedule, item_middleware_instances)
            except Exception:
                spider.logger.error(traceback.format_exc())
                spider.logger.error(f"{spider.spider_name} encountered an exception with request: {request.url}")

        spider.logger.info(f"{spider.spider_name} spider finished")
        await spider.spider_end()

    def _init_middlewares(self):
        """Initialize request and item middleware instances"""
        spider = self.spider
        request_middleware_instances = [
            request_middleware(spider=spider) for request_middleware in spider.request_middlewares
        ]
        item_middleware_instances = [
            item_middleware(spider=spider) for item_middleware in spider.item_middlewares
        ]
        return request_middleware_instances, item_middleware_instances

    async def _handle_request_pipeline(self, request, schedule, item_middleware_instances):
        """Initiate the processing pipeline"""
        spider = self.spider

        # Pass the request to the scheduler for processing
        async for schedule_res in schedule.schedule(request):
            # If the scheduler returns an item
            if isinstance(schedule_res, StableItem):
                stable_item = schedule_res
                await self._process_item(stable_item, item_middleware_instances)

    async def _process_item(self, item, item_middleware_instances):
        spider = self.spider
        for middleware in item_middleware_instances:
            spider.logger.info(
                f"{spider.spider_name} Item middleware {middleware} processing: {item.url}"
            )
            item = await middleware.process_item(item)
            if item is None:
                spider.logger.info(
                    f"{spider.spider_name} Item middleware {middleware} intercepted the item: {item.url}"
                )
                break
