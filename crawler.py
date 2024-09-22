import hashlib
import pickle
from collections import deque
from pathlib import Path
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
        self._queue: deque[str] = deque()
        self.__initialize_directories(DIRECTORY_TO_DOWNLOAD_HTML)

    def crawl(self, start_url: str = None) -> None:
        start_url = self.__initialize_and_validate_url(start_url)
        self._queue.append(start_url)
        while self._queue:
            current_url = self._queue.popleft()
            if current_url in self._visited_links:
                continue
            self._visited_links.add(current_url)
            self.__download(current_url)
            print(current_url)

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

    def set_start_url(self, url: str) -> None:
        if not URL_PATTERN.match(url):
            raise ValueError("Error: Invalid URL")
        self.start_url = url

    def set_allowed_domain(self, domain: str) -> None:
        if not DOMAIN_PATTERN.match(domain):
            raise ValueError("Error: Invalid domain")
        self.allowed_domain = domain

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
        html_code = self._html_getter.get(url)
        if html_code:
            file_name = hashlib.md5(url.encode()).hexdigest() + '.html'
            (folder_name / file_name).write_text(html_code, encoding='utf-8')

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
