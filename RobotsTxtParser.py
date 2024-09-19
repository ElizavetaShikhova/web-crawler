from urllib.parse import urljoin, urlparse
import requests


class RobotsTxtParser:
    def __init__(self, base_url):
        self.base_url = base_url
        self.disallowed_paths = set()

    def get_robots_txt(self):
        robots_url = urljoin(self.base_url, 'robots.txt')
        response = requests.get(robots_url)
        if response.status_code == 200:
            self.parse_robots_txt(response.text)

    def parse_robots_txt(self, content):
        for_all_user_agents = False
        lines = content.splitlines()
        for line in lines:
            if line.startswith('User-agent:'):
                for_all_user_agents = line.split(': ')[1] == '*'
            if line.startswith('Disallow:') and for_all_user_agents:
                disallow_path = line.split(': ')[1]
                self.disallowed_paths.add(disallow_path)

    def is_path_allowed(self, path):
        return path not in self.disallowed_paths

