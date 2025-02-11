from typing import Optional, Union

from core.item import StableItem


class ItemMiddleware:
    def __init__(self, spider: 'Spider'):
        self.spider = spider

    async def process_item(self, item: 'StableItem') -> Optional[Union['StableItem', None]]:
        """
        Process the item.

        Args:
            item: The item to be processed.

        Returns:
            - StableItem: to continue to the next item middleware.
            - None: to discard this item.
        """
        self.spider.logger.info(f"{self.spider.SPIDER_NAME} process item: {item}")

        clean_res = await self.clean_item(item)

        if not clean_res:
            return clean_res

        save_res = await self.save_item(clean_res)
        return save_res

    async def clean_item(self, item: 'StableItem') -> Optional[Union['StableItem', None]]:
        """
        Clean the item.

        Args:
            item: The item to be cleaned.

        Returns:
            - StableItem: if the item passes the cleaning process.
            - None: if the item fails the cleaning process.
        """
        self.spider.logger.info(f"{self.spider.SPIDER_NAME} clean item")

        return item

    async def save_item(self, item: 'StableItem') -> 'StableItem':
        """
        Save the item.

        Args:
            item: The item to be saved.

        Returns:
            - StableItem: the saved item.
        """
        self.spider.logger.info(f"{self.spider.SPIDER_NAME} save item")

        return item
