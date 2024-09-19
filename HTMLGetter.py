from http import HTTPStatus
from typing import Optional

import requests


class HTMLGetter:
    def __init__(self):
        self.html_code = None

    def get(self, url: str) -> Optional[str]:
        response = requests.get(url)
        if response.status_code == HTTPStatus.OK:
            self.html_code = response.text
        return self.html_code
