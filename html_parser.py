from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

from robots_txt_parser import RobotsTxtParser


class Parser(HTMLParser):
    def __init__(self, base_url: str, robots_parser: RobotsTxtParser) -> None:
        super().__init__()
        self.base_url = base_url
        self.robots_parser = robots_parser
        self.links = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str | None]]) -> None:
        if tag != 'a':
            return
        for attr in attrs:
            if attr[0] != 'href':
                continue
            absolute_url = urljoin(self.base_url, attr[1])
            parsed_url = urlparse(absolute_url)
            if parsed_url.netloc == urlparse(self.base_url).netloc:
                if self.robots_parser.is_path_allowed(parsed_url.path):
                    self.links.append(absolute_url)
