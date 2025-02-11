# Stable Spider
[English](README.md) | [中文](README.zh.md)

**Stable Spider** is a simple, clear, and extensible Scrapy-like web crawling framework built with Python. It supports asynchronous scraping, Selenium integration, request/response middleware, and robust logging, allowing you to build stable and efficient crawlers quickly.

## ✨ Features

-   **Asynchronous Crawling**: Built on `asyncio` and `httpx` for high-concurrency HTTP requests.
-   **Modular Architecture**: Core components include Request, Response, Spider, Scheduler, Downloader, and Engine.
-   **Middleware Support**: Easily extend request and item processing via custom middleware.
-   **Selenium Integration**: Use `SeleniumSpider` for crawling JavaScript-rendered pages.
-   **Automatic Retry Mechanism**: Built-in synchronous and asynchronous retry decorators to improve stability.
-   **Logging Management**: Supports time-based rotating logs for easier debugging and monitoring.

## 📦 Installation

1.  **Clone the Repository**

    ```
    git clone https://github.com/yourusername/stable_spider.git
    cd stable_spider
    ```

2.  **Install Dependencies**

    Ensure you have Python **3.7 or higher**, then install the required dependencies:

    ```
    pip install -r requirements.txt
    ```

    >   **Note**: If you plan to use Selenium, make sure you have the appropriate browser drivers installed, such as ChromeDriver.

## 🚀 Quick Start

You can create your custom spider by subclassing `Spider` (or `SeleniumSpider` for Selenium support) and implementing the required methods:

```python
import asyncio
from stable_spider.core.engine import Engine
from stable_spider.core.spider import Spider
from stable_spider.core.request import StableRequest
from stable_spider.core.response import StableResponse

class MySpider(Spider):
    SPIDER_NAME = "MySpider"
    START_URL_LIST = [
        "https://www.example.com",
        "https://httpbin.org/get",
    ]

    # Define initial requests
    async def start_request(self):
        for url in self.START_URL_LIST:
            yield StableRequest(url=url, method='GET', callback=self.parse)

    # Parse the response
    async def parse(self, response: StableResponse):
        print(f"Fetched {response.url} with status {response.status_code}")
        return None  # You can return new requests or items if needed

if __name__ == "__main__":
    spider = MySpider()
    engine = Engine(spider)
    asyncio.run(engine.start())
```

## 📂 Project Structure

```
stable_spider/
├── core/
│   ├── engine.py              # The main crawling engine
│   ├── item.py                # Item definitions and processing
│   ├── request.py             # Request wrapper (supports HTTP and Selenium)
│   ├── response.py            # Response wrapper with parsing utilities
│   ├── schedule.py            # Scheduler for handling request queues
│   └── spider.py              # Base Spider class for customization
├── middlewares/
│   ├── item_middleware.py     # Middleware for processing scraped items
│   └── request_middleware.py  # Middleware for handling requests and responses
├── utils/
│   ├── retry.py               # Automatic retry decorators
│   └── selenium_driver.py     # Selenium driver utilities
├── log.py                     # Logging configuration
└── README.md                  # Project documentation
```

## ⚙️ Configuration

-   **Logging**:
    Logging is configured via the environment variables `LOG_DIR_PATH` and `PROJECT_NAME`. By default, logs are stored in the `./logs` directory, and the project name is set to `"project"`.
-   **Custom Middleware**:
    Add custom `RequestMiddleware` or `ItemMiddleware` by appending them to the `REQUEST_MIDDLEWARES` and `ITEM_MIDDLEWARES` lists in your spider class.
-   **Selenium Support**:
    Use `SeleniumSpider` instead of `Spider` to enable Selenium-based crawling and configure the necessary Selenium options (browser type, grid hub URL, etc.).

## 🤝 Contributing

We welcome contributions! Feel free to submit an issue or a pull request:

1.  **Fork this repository** and create a new branch.
2.  Implement your changes and **submit a Pull Request**.
3.  We will review and merge your changes as soon as possible. 🎉

## 📜 License

This project is licensed under the **Apache License 2.0**.
See the full license here: [Apache License 2.0](http://www.apache.org/licenses/).