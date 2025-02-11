from pydantic import BaseModel


class StableItem(BaseModel):

    @classmethod
    async def create_item(cls, **kwargs):
        return cls(**kwargs)
