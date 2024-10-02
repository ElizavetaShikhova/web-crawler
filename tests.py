import unittest
from http import HTTPStatus
from unittest.mock import patch, MagicMock, Mock
import requests
import time

from crawler import Crawler
from html_getter import HTMLGetter
from url_patterns import URL_PATTERN, DOMAIN_PATTERN
from robots_txt_parser import RobotsTxtParser
from html_parser import Parser


class TestHTMLGetter(unittest.TestCase):
    @patch('requests.get')
    def test_get_success(self, mock_get):
        # Подготовка мок-объекта для имитации успешного ответа
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.text = "Mocked HTML content"
        mock_get.return_value = mock_response

        html_getter = HTMLGetter()
        result = html_getter.get("http://example.com")

        self.assertEqual(result, "Mocked HTML content")
        mock_get.assert_called_once_with("http://example.com", timeout=10)

    @patch('requests.get')
    def test_get_not_found(self, mock_get):
        # Подготовка мок-объекта для имитации ответа с ошибкой 404
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.NOT_FOUND
        mock_get.return_value = mock_response

        html_getter = HTMLGetter()
        result = html_getter.get("http://example.com/not_found")

        self.assertIsNone(result)
        mock_get.assert_called_once_with("http://example.com/not_found", timeout=10)

    @patch('requests.get')
    @patch('sys.exit')
    def test_get_request_exception(self, mock_exit, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Network error")
        mock_exit.side_effect = SystemExit

        html_getter = HTMLGetter()
        with self.assertRaises(SystemExit):
            html_getter.get("http://example.com/error")

        mock_get.assert_called_once_with("http://example.com/error", timeout=10)
        mock_exit.assert_called_once()

    @patch('requests.get')
    @patch('sys.exit')
    def test_get_timeout_exception(self, mock_exit, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")
        mock_exit.side_effect = SystemExit

        html_getter = HTMLGetter()
        with self.assertRaises(SystemExit):
            html_getter.get("http://example.com/timeout")

        mock_get.assert_called_once_with("http://example.com/timeout", timeout=10)
        mock_exit.assert_called_once()

class TestRegex(unittest.TestCase):
    def test_url_pattern_valid(self):
        valid_urls = [
            "http://example.com",
            "https://www.example.com",
            "ftp://example.com",
            "http://example.com:8080",
            "http://example.com/path/to/resource",
            "http://example.com/path?query=string",
            "http://example.com:8080/path?query=string",
        ]
        for url in valid_urls:
            with self.subTest(url=url):
                self.assertIsNotNone(URL_PATTERN.match(url))

    def test_url_pattern_invalid(self):
        invalid_urls = [
            "example.com",
            "http://",
            "http://example",
            "http://example.com:abc",
            "http://example.com/path#fragment",
        ]
        for url in invalid_urls:
            with self.subTest(url=url):
                self.assertIsNone(URL_PATTERN.match(url))

    def test_domain_pattern_valid(self):
        valid_domains = [
            "example.com",
            "www.example.com",
            "sub.example.com",
            "example.co.uk",
            "example-domain.com",
        ]
        for domain in valid_domains:
            with self.subTest(domain=domain):
                self.assertIsNotNone(DOMAIN_PATTERN.match(domain))

    def test_domain_pattern_invalid(self):
        invalid_domains = [
            "example",
            "example.c",
            "example.com/",
            "example.com:8080",
            "-example.com",
            "example-.com",
        ]
        for domain in invalid_domains:
            with self.subTest(domain=domain):
                self.assertIsNone(DOMAIN_PATTERN.match(domain), f"Domain {domain} should be invalid")

class TestHTMLParser(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://example.com"
        self.disallowed_paths = {"/page3", "/page4"}
        self.robots_parser = RobotsTxtParser(self.base_url, self.disallowed_paths)
        self.parser = Parser(self.base_url, self.robots_parser)

    def test_handle_starttag_with_allowed_links(self):
        html = '<a href="/page1">Page 1</a><a href="/page2">Page 2</a>'
        self.parser.feed(html)
        self.assertEqual(self.parser.links, ["http://example.com/page1", "http://example.com/page2"])

    def test_handle_starttag_with_disallowed_links(self):
        html = '<a href="/page3">Page 3</a><a href="/page4">Page 4</a>'
        self.parser.feed(html)
        self.assertEqual(self.parser.links, [])

    def test_handle_starttag_with_mixed_links(self):
        html = '<a href="/page1">Page 1</a><a href="/page3">Page 3</a>'
        self.parser.feed(html)
        self.assertEqual(self.parser.links, ["http://example.com/page1"])

    def test_extract_text_simple(self):
        html = '<p>Hello, world!</p>'
        self.parser.feed(html)
        self.assertEqual(self.parser.get_extract_text(), "Hello, world!")

    def test_extract_text_with_nested_tags(self):
        html = '<div><h1>Title</h1><p>Paragraph text.</p></div>'
        self.parser.feed(html)
        self.assertEqual(self.parser.get_extract_text(), "Title Paragraph text.")

    def test_extract_text_with_script_and_style(self):
        html = '<style>body { font-size: 12px; }</style><script>alert("Hi!");</script><p>Visible text.</p>'
        self.parser.feed(html)
        self.assertEqual(self.parser.get_extract_text(), "Visible text.")

    def test_extract_text_with_multiple_elements(self):
        html = '<div>First part.</div><p>Second part.</p><span>Third part.</span>'
        self.parser.feed(html)
        self.assertEqual(self.parser.get_extract_text(), "First part. Second part. Third part.")

    def test_extract_text_with_empty_tags(self):
        html = '<div></div><p></p><span></span>'
        self.parser.feed(html)
        self.assertEqual(self.parser.get_extract_text(), "")

    def test_extract_text_with_line_breaks(self):
        html = '<p>Line 1<br>Line 2<br>Line 3</p>'
        self.parser.feed(html)
        self.assertEqual(self.parser.get_extract_text(), "Line 1 Line 2 Line 3")

    def test_handle_starttag_with_external_links(self):
        html = '<a href="http://external.com/page1">External Page 1</a>'
        self.parser.feed(html)
        self.assertEqual(self.parser.links, [])

    def test_handle_starttag_with_relative_links(self):
        html = '<a href="page1">Page 1</a>'
        self.parser.feed(html)
        self.assertEqual(self.parser.links, ["http://example.com/page1"])

    def test_handle_starttag_with_invalid_tags(self):
        html = '<div href="/page1">Invalid Tag</div>'
        self.parser.feed(html)
        self.assertEqual(self.parser.links, [])

class TestRobotsTxtParser(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://example.com"
        self.disallowed_paths = {"/disallowed1", "/disallowed2"}
        self.parser = RobotsTxtParser(self.base_url, self.disallowed_paths)

    def test_is_path_allowed_with_allowed_path(self):
        self.assertTrue(self.parser.is_path_allowed("/allowed1"))

    def test_is_path_allowed_with_disallowed_path(self):
        self.assertFalse(self.parser.is_path_allowed("/disallowed1"))

    @patch('requests.get')
    def test_fetch_robots_txt_with_valid_content(self, mock_get):
        robots_txt_content = """
            User-agent: *
            Disallow: /disallowed1
            Disallow: /disallowed2
            """
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.text = robots_txt_content
        mock_get.return_value = mock_response

        self.parser.fetch_robots_txt()
        self.assertEqual(self.parser._disallowed_paths, {"/disallowed1", "/disallowed2"})

    @patch('requests.get')
    def test_fetch_robots_txt_with_invalid_content(self, mock_get):
        robots_txt_content = """
            User-agent: *
            Disallow: /disallowed1
            Disallow: /disallowed2
            User-agent: specific-agent
            Disallow: /specific-disallowed
            """
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.text = robots_txt_content
        mock_get.return_value = mock_response

        self.parser.fetch_robots_txt()
        self.assertEqual(self.parser._disallowed_paths, {"/disallowed1", "/disallowed2"})

    @patch('requests.get')
    def test_fetch_robots_txt_with_no_disallowed_paths(self, mock_get):
        parser = RobotsTxtParser(self.base_url)
        robots_txt_content = """
            User-agent: *
            """
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.text = robots_txt_content
        mock_get.return_value = mock_response

        parser.fetch_robots_txt()
        self.assertEqual(parser._disallowed_paths, set())

    @patch('requests.get')
    def test_fetch_robots_txt_with_mock_response(self, mock_get):
        robots_txt_content = """
            User-agent: *
            Disallow: /disallowed1
            Disallow: /disallowed2
            """
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.text = robots_txt_content
        mock_get.return_value = mock_response

        self.parser.fetch_robots_txt()
        self.assertEqual(self.parser._disallowed_paths, {"/disallowed1", "/disallowed2"})

class TestCrawler(unittest.TestCase):
    def setUp(self):
        self.crawler = Crawler()

    def test_set_start_url_valid(self):
        self.crawler.set_start_url("http://example.com")
        self.assertEqual(self.crawler.start_url, "http://example.com")

    def test_set_start_url_invalid(self):
        with self.assertRaises(ValueError):
            self.crawler.set_start_url("invalid_url")

    def test_set_allowed_domain_valid(self):
        self.crawler.set_allowed_domain("example.com")
        self.assertEqual(self.crawler.allowed_domain, "example.com")

    def test_set_allowed_domain_invalid(self):
        with self.assertRaises(ValueError):
            self.crawler.set_allowed_domain("invalid_domain")

    @patch('builtins.print')
    def test_crawl_with_start_url(self, mock_print):
        self.crawler.set_start_url("http://example.com")
        self.crawler.crawl()
        self.assertIn("http://example.com", self.crawler._visited_links)
        mock_print.assert_called_with("http://example.com")

    @patch('builtins.print')
    def test_crawl_with_no_start_url(self, mock_print):
        with self.assertRaises(ValueError):
            self.crawler.crawl()

    @patch('builtins.print')
    def test_crawl_with_allowed_domain(self, mock_print):
        self.crawler.set_start_url("http://example.com")
        self.crawler.set_allowed_domain("example.com")
        self.crawler.crawl()
        self.assertIn("http://example.com", self.crawler._visited_links)
        mock_print.assert_called_with("http://example.com")

    @patch('builtins.print')
    def test_crawl_with_disallowed_domain(self, mock_print):
        self.crawler.set_start_url("http://example.com")
        self.crawler.set_allowed_domain("anotherdomain.com")
        self.crawler.crawl()
        self.assertNotIn("http://example.com", self.crawler._visited_links)
        mock_print.assert_not_called()

    @patch('builtins.print')
    def test_crawl_with_visited_link(self, mock_print):
        self.crawler.set_start_url("http://example.com")
        self.crawler._visited_links.add("http://example.com")
        self.crawler.crawl()
        self.assertNotIn("http://example.com/page1", self.crawler._visited_links)
        mock_print.assert_not_called()

    @patch('builtins.print')
    def test_crawl_with_no_html_code(self, mock_print):
        self.crawler.set_start_url("http://example.com")
        self.crawler._html_getter.get = Mock(return_value=None)
        self.crawler.crawl()
        self.assertIn("http://example.com", self.crawler._visited_links)
        mock_print.assert_called_with("http://example.com")

    @patch('builtins.print')
    def test_crawl_with_no_links(self, mock_print):
        self.crawler.set_start_url("http://example.com")
        self.crawler._html_getter.get = Mock(return_value="<html><body></body></html>")
        self.crawler.crawl()
        self.assertIn("http://example.com", self.crawler._visited_links)
        mock_print.assert_called_with("http://example.com")


if __name__ == '__main__':
    unittest.main()
