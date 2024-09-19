import requests

class HTMLGetter:
    def __init__(self):
        self.html_code = None

    def get(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            self.html_code = response.text

    def is_page_found(self):
        return self.html_code != None




