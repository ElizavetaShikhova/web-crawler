import hashlib
import re
from pathlib import Path
from urllib.parse import urlparse

from HTMLGetter import HTMLGetter
from HTMLParser import Parser
from RobotsTxtParser import RobotsTxtParser


class Crawler:
    def __init__(self):
        self.visited_links = set()
        self.robots_parsers = {}
        self.allowed_domain = None
        self.start_url = None
        if not Path('./htmlPages').exists():
            Path('./htmlPages').mkdir(parents=True)

    def crawl(self, start_url=None):
        if start_url is None:
            if self.start_url is None:
                raise ValueError("Error: Start URL is not set.")
            start_url = self.start_url
        self.visited_links.add(start_url)
        self.download(start_url)
        print(start_url)
        base_url = urlparse(start_url).scheme + '://' + urlparse(start_url).netloc
        if base_url not in self.robots_parsers:
            robots_parser = RobotsTxtParser(base_url)
            robots_parser.get_robots_txt()
            self.robots_parsers[base_url] = robots_parser
        else:
            robots_parser = self.robots_parsers[base_url]

        html_getter = HTMLGetter()
        html_getter.get(start_url)
        if html_getter.is_page_found():
            parser = Parser(base_url, robots_parser)
            parser.feed(html_getter.html_code)  # парсинг html кода -> нахождение ссылок
            for link in parser.links:
                if link not in self.visited_links:
                    if not self.allowed_domain or (
                            self.allowed_domain and self.allowed_domain == urlparse(link).netloc):
                        self.crawl(link)

    def download(self, url):
        folder_name = urlparse(url).netloc
        if not Path(f'./htmlPages/{folder_name}').exists():
            Path(f'./htmlPages/{folder_name}').mkdir()
        html_getter = HTMLGetter()
        html_getter.get(url)
        if html_getter.html_code:
            file_name = hashlib.md5(url.encode()).hexdigest() + '.html'
            Path(f'./htmlPages/{folder_name}/{file_name}').write_text(
                html_getter.html_code, encoding='utf-8')

    def set_start_url(self, url):
        url_pattern = re.compile(
            r'^(https?|ftp)://'  # Протокол
            r'([A-Za-z0-9.-]+)'  # Домен
            r'(:\d+)?'  # Порт (опционально)
            r'(/[^?#]*)?'  # Путь (опционально)
            r'(\?[^#]*)?$'  # Параметры (опционально)
        )
        if url_pattern.match(url):
            self.start_url = url
        else:
            raise ValueError("Error: Invalid URL")

    def set_allowed_domain(self, domain):
        domain_pattern = re.compile(
            r'^([A-Za-z0-9-]+\.)+[A-Za-z]{2,}$'
        )
        if domain_pattern.match(domain):
            self.allowed_domain = domain
        else:
            raise ValueError("Error: Invalid domain")
