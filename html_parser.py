from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

import requests

from robots_txt_parser import RobotsTxtParser


class Parser(HTMLParser):
    def __init__(self, base_url: str, robots_parser: RobotsTxtParser) -> None:
        super().__init__()
        self.base_url = base_url
        self.robots_parser = robots_parser
        self.links = []
        self.max_image_size_on_page: int = 0
        self.text_content = []
        self.ignore_text: bool = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str | None]]) -> None:
        if tag in ('script', 'style'):
            self.ignore_text = True
        if tag == 'a':
            for attr in attrs:
                if attr[0] == 'href':
                    absolute_url = urljoin(self.base_url, attr[1])
                    parsed_url = urlparse(absolute_url)
                    if parsed_url.netloc == urlparse(self.base_url).netloc:
                        if self.robots_parser.is_path_allowed(parsed_url.path):
                            self.links.append(absolute_url)
        elif tag == 'img':
            for attr in attrs:
                if attr[0] == 'src':
                    image_url = urljoin(self.base_url, attr[1])
                    self.__count_image_size(image_url)

    def handle_endtag(self, tag: str) -> None:
        if tag in ('script', 'style'):
            self.ignore_text = False

    def handle_data(self, data: str) -> None:
        if not self.ignore_text:
            self.text_content.append(data)

    def get_extract_text(self) -> str:
        return ' '.join(self.text_content).strip()

    def __count_image_size(self, image_url: str) -> None:
        try:
            response = requests.head(image_url)
            response.raise_for_status()
            content_length = int(response.headers.get('Content-Length', 0))
            self.max_image_size_on_page = max(content_length, self.max_image_size_on_page)
        except Exception:
            return
