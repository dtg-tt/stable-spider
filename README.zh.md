# Stable Spider

[English](README.md) | [中文](README.zh.md)

**Stable Spider** 是一个简单、清晰且可扩展的 Scrapy-like 爬虫框架，基于 Python 构建，支持异步爬取、Selenium
集成、请求/响应中间件以及日志管理，帮助你快速搭建高效稳定的爬虫。

## ✨ 特性

- **异步爬取**：基于 `asyncio` 和 `httpx` 进行高并发 HTTP 请求。
- **模块化架构**：核心组件包括 Request、Response、Spider、Scheduler、Downloader 和 Engine。
- **中间件支持**：支持自定义请求和数据处理中间件，便于扩展功能。
- **Selenium 集成**：提供 `SeleniumSpider` 以支持动态渲染页面的爬取。
- **自动重试机制**：内置同步和异步的请求重试装饰器，提高稳定性。
- **日志管理**：支持基于时间滚动的日志存储，方便调试和监控。

## 📦 安装

1. **克隆项目**

   ```
   bash复制编辑git clone https://github.com/yourusername/stable_spider.git
   cd stable_spider
   ```

2. **安装依赖**

   确保你的 Python 版本 **≥ 3.7**，然后安装所需依赖：

   ```
   bash
   
   
   复制编辑
   pip install -r requirements.txt
   ```

   > **注意**：如果需要使用 Selenium，请确保已安装相应的浏览器驱动，例如 ChromeDriver。

## 🚀 快速开始

你可以继承 `Spider`（或 `SeleniumSpider`）来自定义爬虫，并实现相应的方法：

```
python复制编辑import asyncio
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

    # 定义起始请求
    async def start_request(self):
        for url in self.START_URL_LIST:
            yield StableRequest(url=url, method='GET', callback=self.parse)

    # 解析响应
    async def parse(self, response: StableResponse):
        print(f"Fetched {response.url} with status {response.status_code}")
        return None  # 可以返回新的请求或数据项

if __name__ == "__main__":
    spider = MySpider()
    engine = Engine(spider)
    asyncio.run(engine.start())
```

## 📂 目录结构

```
plaintext复制编辑stable_spider/
├── core/
│   ├── engine.py              # 爬虫调度引擎
│   ├── item.py                # 数据项定义及处理
│   ├── request.py             # 请求封装（支持 HTTP 和 Selenium）
│   ├── response.py            # 响应封装，支持 XPath/JSON 解析
│   ├── schedule.py            # 调度器，管理请求队列
│   └── spider.py              # 基础 Spider 类，可继承自定义
├── middlewares/
│   ├── item_middleware.py     # Item 处理中间件
│   └── request_middleware.py  # 请求/响应处理中间件
├── utils/
│   ├── retry.py               # 自动重试装饰器
│   └── selenium_driver.py     # Selenium 驱动封装
├── log.py                     # 日志管理
└── README.md                  # 项目文档
```

## ⚙️ 配置说明

- **日志管理**：可以通过环境变量 `LOG_DIR_PATH` 和 `PROJECT_NAME` 进行配置，默认日志存储在 `./logs`
  目录下，项目名称默认为 `project`。
- **自定义中间件**：在爬虫类中，将自定义 `RequestMiddleware` 或 `ItemMiddleware` 添加到 `REQUEST_MIDDLEWARES`
  和 `ITEM_MIDDLEWARES` 变量中。
- **Selenium 支持**：使用 `SeleniumSpider` 代替 `Spider`，并传入 Selenium 相关配置。

## 🤝 贡献指南

欢迎贡献代码或提交 Issue ！你可以通过以下方式参与：

1. **Fork 本仓库** 并创建新分支
2. 提交你的更改，并 **创建 Pull Request**
3. 我们会尽快 Review 并合并 🎉

## 📜 许可证

本项目基于 **Apache License 2.0** 进行开源。
完整许可证信息请查看 [Apache License 2.0](http://www.apache.org/licenses/).