from http import HTTPStatus
from urllib.parse import urljoin

import requests


class RobotsTxtParser:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self._disallowed_paths = set()

    def get_robots_txt(self) -> None:
        robots_url = urljoin(self.base_url, 'robots.txt')
        response = requests.get(robots_url)
        if response.status_code == HTTPStatus.OK:
            self.__parse_robots_txt(response.text)

    def is_path_allowed(self, path: str) -> bool:
        return path not in self.disallowed_paths

    def __parse_robots_txt(self, content: str) -> None:
        for_all_user_agents = False
        lines = content.splitlines()
        for line in lines:
            if line.startswith('User-agent:'):
                for_all_user_agents = line.split(': ')[1] == '*'
            if line.startswith('Disallow:') and for_all_user_agents:
                disallow_path = line.split(': ')[1]
                self.disallowed_paths.add(disallow_path)

    @property
    def disallowed_paths(self):
        return self._disallowed_paths

    @disallowed_paths.setter
    def disallowed_paths(self, value):
        self._disallowed_paths = value
