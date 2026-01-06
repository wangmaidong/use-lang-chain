import os

from sqlalchemy.testing.suite.test_reflection import metadata

from ..documents import Document
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from urllib.parse import urlparse
import ssl
from typing import List


class WebBaseLoader:
    def __init__(self, web_paths: List[str]):
        self.web_paths = web_paths

    def _scrape(self, url):
        # 构建请求对象
        request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        # 打开URL地址并获取响应
        with urlopen(request) as response:
            html_content = response.read()
            encoding = response.headers.get_content_charset() or "utf-8"
            html_text = html_content.decode(encoding, errors="ignore")
        # 用BeautifulSoup来解析HTML文档
        soup = BeautifulSoup(html_text, "html.parser")
        # 移除 script和style标签
        for script in soup(["script", "style"]):
            script.decompose()
        title_tag = soup.find("title")
        title = title_tag.get_text().strip() if title_tag else ""
        html_tag = soup.find("html")
        # 获取lang属性作为语言，没有的话就用en
        language = html_tag.get("lang", "en") if html_tag else "en"
        # 提取网页的正文，所有的可见的文本，按换行符分隔
        text_content = soup.get_text(separator="\n", strip=True)
        return {"content": text_content, "title": title, "language": language}

    def load(self):
        docs = []
        for url in self.web_paths:
            # 遍历抓取网页的内容
            scraped_data = self._scrape(url)
            metadata = {
                "source": url,
                "title": scraped_data["title"],
                "language": scraped_data["language"],
            }
            docs.append(
                Document(page_content=scraped_data["content"], metadata=metadata)
            )
        return docs
