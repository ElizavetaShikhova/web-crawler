import hashlib
import pickle
from collections import deque
from os import path
from pathlib import Path
from time import time
from urllib.parse import urlparse

from html_getter import HTMLGetter
from html_parser import Parser
from robots_txt_parser import RobotsTxtParser
from url_patterns import URL_PATTERN, DOMAIN_PATTERN

DIRECTORY_TO_DOWNLOAD_HTML = Path('./htmlPages')
STATE_FILE = Path('crawler_state.pkl')


class Crawler:
    def __init__(self) -> None:
        self._visited_links = set()
        self._robots_parsers = {}
        self._html_getter = HTMLGetter()
        self.allowed_domain: str | None = None
        self.start_url: str | None = None
        self.update_flag: bool = False
        self.update_interval: int = 3600
        self._queue: deque[str] = deque()
        self.__initialize_directories(DIRECTORY_TO_DOWNLOAD_HTML)

    def crawl(self, start_url: str = None) -> None:
        start_url = self.__initialize_and_validate_url(start_url)
        if self.__check_is_allowed_link(start_url):
            self._queue.append(start_url)
        while self._queue:
            current_url = self._queue.popleft()
            if current_url in self._visited_links:
                continue
            self._visited_links.add(current_url)
            self.__download(current_url)

            base_url = urlparse(current_url).scheme + '://' + urlparse(current_url).netloc
            robots_parser = self.__load_robots_txt(base_url)
            html_code = self._html_getter.get(current_url)
            if not html_code:
                continue
            links = self.__parse_html(base_url, robots_parser, html_code)
            for link in links:
                if self.__check_is_allowed_link(link):
                    self._queue.append(link)
                    save_state(self)
        if self.update_flag:
            self._visited_links = set()

    def set_start_url(self, url: str) -> None:
        if not URL_PATTERN.match(url):
            raise ValueError("Error: Invalid URL")
        self.start_url = url

    def set_allowed_domain(self, domain: str) -> None:
        if not DOMAIN_PATTERN.match(domain):
            raise ValueError("Error: Invalid domain")
        self.allowed_domain = domain

    def set_update(self, update_flag: bool) -> None:
        self.update_flag = update_flag

    def set_update_interval(self, interval: int) -> None:
        self.update_interval = interval

    def __initialize_directories(self, directory: Path) -> None:
        if not directory.exists():
            directory.mkdir(parents=True)

    def __check_is_allowed_link(self, link: str) -> bool:
        return link not in self._visited_links and (
                not self.allowed_domain or (self.allowed_domain and self.allowed_domain == urlparse(link).netloc))

    def __download(self, url: str) -> None:
        folder_name = urlparse(url).netloc
        folder_name = DIRECTORY_TO_DOWNLOAD_HTML / folder_name
        self.__initialize_directories(folder_name)
        file_name = hashlib.md5(url.encode()).hexdigest() + '.html'
        file_path = folder_name / file_name
        if file_path.exists():
            file_mtime = path.getmtime(file_path)
            current_time = time()
            if current_time - file_mtime < self.update_interval:
                print(f"Skipping {url} as it was recently updated.")
                return
        html_code = self._html_getter.get(url)
        if html_code:
            file_path.write_text(html_code, encoding='utf-8')
            print(f"Downloaded {url}")

    def __initialize_and_validate_url(self, start_url: str | None) -> str:
        if start_url is None:
            if self.start_url is None:
                raise ValueError("Error: Start URL is not set.")
            start_url = self.start_url
        return start_url

    def __load_robots_txt(self, base_url: str) -> RobotsTxtParser:
        if base_url not in self._robots_parsers:
            robots_parser = RobotsTxtParser(base_url)
            robots_parser.fetch_robots_txt()
            self._robots_parsers[base_url] = robots_parser
        else:
            robots_parser = self._robots_parsers[base_url]
        return robots_parser

    def __parse_html(self, base_url: str, robots_parser: RobotsTxtParser, html_code: str) -> list[str]:
        parser = Parser(base_url, robots_parser)
        parser.feed(html_code)
        return parser.links


def save_state(crawler: Crawler) -> None:
    with open(STATE_FILE, 'wb') as f:
        pickle.dump(crawler, f)


def load_state() -> Crawler | None:
    if STATE_FILE.exists():
        with open(STATE_FILE, 'rb') as f:
            return pickle.load(f)
