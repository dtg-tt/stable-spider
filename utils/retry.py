import asyncio
import time
from functools import wraps


def retry(max_retries=3, delay=5, exceptions=(Exception,)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            # Check whether retry is needed
            if kwargs.get("need_retry") is not None:
                if not kwargs.get("need_retry"):
                    return func(*args, **kwargs)

            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    if retries > max_retries:
                        print("Maximum retry limit reached, operation still failed")
                        raise e
                    print(f"Exception occurred: {e}, retrying for the {retries} time, waiting for {delay} seconds")
                    time.sleep(delay)

        return wrapper

    return decorator


def async_retry(max_retries=3, delay=5, exceptions=(Exception,)):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            retries = 0
            while True:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    if retries > max_retries:
                        print("Maximum retry limit reached, operation still failed")
                        raise e
                    print(e)
                    print(f"Exception occurred: {e}, retrying for the {retries} time, waiting for {delay} seconds")
                    await asyncio.sleep(delay)

        return wrapper

    return decorator
