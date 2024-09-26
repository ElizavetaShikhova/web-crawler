import sys
from http import HTTPStatus

import requests
from requests.exceptions import RequestException


class HTMLGetter:
    def get(self, url: str) -> str | None:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == HTTPStatus.OK:
                return response.text
        except RequestException as e:
            print(f"Error fetching URL {url}: {e}")
            sys.exit()

