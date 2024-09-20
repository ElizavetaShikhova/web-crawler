import sys

import requests
from requests.exceptions import RequestException
from http import HTTPStatus
from typing import Optional


class HTMLGetter:
    def __init__(self):
        self.html_code = None

    def get(self, url: str) -> Optional[str]:
        try:
            response = requests.get(url)
            if response.status_code == HTTPStatus.OK:
                self.html_code = response.text
            return self.html_code
        except RequestException as e:
            print(f"Error fetching URL {url}: {e}")
            sys.exit()
