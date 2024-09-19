from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

class Parser(HTMLParser):
    def __init__(self, base_url, robots_parser):
        super().__init__()
        self.base_url = base_url
        self.robots_parser = robots_parser
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr in attrs:
                if attr[0] == 'href':
                    absolute_url = urljoin(self.base_url, attr[1])
                    parsed_url = urlparse(absolute_url)
                    if parsed_url.netloc == urlparse(self.base_url).netloc:
                        if self.robots_parser.is_path_allowed(parsed_url.path):
                            self.links.append(absolute_url)

    '''def get_links(self):
        return self.links'''