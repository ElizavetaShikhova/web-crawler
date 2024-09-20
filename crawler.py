import hashlib
import pickle
from collections import deque
from pathlib import Path
from typing import Optional, Deque
from urllib.parse import urlparse

from HTMLGetter import HTMLGetter
from HTMLParser import Parser
from URLPatterns import URLPatterns
from robotsTxtParser import RobotsTxtParser

DIRECTORY_TO_DOWNLOAD_HTML = './htmlPages'
STATE_FILE = 'crawler_state.pkl'


class Crawler:
    def __init__(self) -> None:
        self._visited_links = set()
        self._robots_parsers = {}
        self._html_getter = HTMLGetter()
        self._patterns = URLPatterns()
        self.allowed_domain = None
        self.start_url = None
        self._queue: Deque[str] = deque()
        self.__initialize_directories(DIRECTORY_TO_DOWNLOAD_HTML)

    def crawl(self, start_url: str = None) -> None:
        start_url = self.__initialize_and_validate_url(start_url)
        self.queue.append(start_url)
        while self.queue:
            current_url = self.queue.popleft()
            if current_url in self.visited_links:
                continue
            self.visited_links.add(current_url)
            self.__download(current_url)
            print(current_url)

            base_url = urlparse(current_url).scheme + '://' + urlparse(current_url).netloc
            robots_parser = self.__load_robots_txt(base_url)
            html_code = self.html_getter.get(current_url)
            if not html_code:
                continue
            links = self.__parse_html(base_url, robots_parser, html_code)
            for link in links:
                if self.__check_is_allowed_link(link):
                    self.queue.append(link)
                    save_state(self)

    def set_start_url(self, url: str) -> None:
        if not self.patterns.URL_PATTERN.match(url):
            raise ValueError("Error: Invalid URL")
        self.start_url = url

    def set_allowed_domain(self, domain: str) -> None:
        if not self.patterns.DOMAIN_PATTERN.match(domain):
            raise ValueError("Error: Invalid domain")
        self.allowed_domain = domain

    def __initialize_directories(self, directory: str) -> None:
        if not Path(directory).exists():
            Path(directory).mkdir(parents=True)

    def __check_is_allowed_link(self, link: str) -> bool:
        return link not in self.visited_links and (
                not self.allowed_domain or (self.allowed_domain and self.allowed_domain == urlparse(link).netloc))

    def __download(self, url: str) -> None:
        folder_name = urlparse(url).netloc
        self.__initialize_directories(f'{DIRECTORY_TO_DOWNLOAD_HTML}/{folder_name}')
        html_code = self.html_getter.get(url)
        if html_code:
            file_name = hashlib.md5(url.encode()).hexdigest() + '.html'
            Path(f'./htmlPages/{folder_name}/{file_name}').write_text(html_code, encoding='utf-8')

    def __initialize_and_validate_url(self, start_url: str) -> str:
        if start_url is None:
            if self.start_url is None:
                raise ValueError("Error: Start URL is not set.")
            start_url = self.start_url
        return start_url

    def __load_robots_txt(self, base_url: str) -> RobotsTxtParser:
        if base_url not in self.robots_parsers:
            robots_parser = RobotsTxtParser(base_url)
            robots_parser.get_robots_txt()
            self.robots_parsers[base_url] = robots_parser
        else:
            robots_parser = self.robots_parsers[base_url]
        return robots_parser

    def __parse_html(self, base_url: str, robots_parser: RobotsTxtParser, html_code: str) -> list[str]:
        parser = Parser(base_url, robots_parser)
        parser.feed(html_code)
        return parser.links

    @property
    def visited_links(self):
        return self._visited_links

    @visited_links.setter
    def visited_links(self, value):
        self._visited_links = value

    @property
    def robots_parsers(self):
        return self._robots_parsers

    @robots_parsers.setter
    def robots_parsers(self, value):
        self._robots_parsers = value

    @property
    def html_getter(self):
        return self._html_getter

    @html_getter.setter
    def html_getter(self, value):
        self._html_getter = value

    @property
    def patterns(self):
        return self._patterns

    @property
    def queue(self):
        return self._queue

    @queue.setter
    def queue(self, value):
        self._queue = value


def save_state(crawler: Crawler) -> None:
    with open(STATE_FILE, 'wb') as f:
        pickle.dump(crawler, f)


def load_state() -> Optional[Crawler]:
    if Path(STATE_FILE).exists():
        with open(STATE_FILE, 'rb') as f:
            return pickle.load(f)
