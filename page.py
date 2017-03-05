from bs4 import BeautifulSoup
from urlparse import urljoin, parse_qsl

class Page(object):
    def __init__(self, response):
        assert hasattr(response, 'request')
        self.request = response.request
        self.html = response.text
        self.headers = response.headers
        self.status_code = response.status_code
        self.document = BeautifulSoup(self.html, 'html.parser')

    @property
    def url(self):
        return self.request.url

    @property
    def url_parameters(self):
        _, _, url = self.url.partition("?")
        return parse_qsl(url)

    def get_links(self, blacklist=[]):
        """ Generator for all links on the page. """
        for href in [h.get('href') for h in self.document.find_all('a')]:
            url = urljoin(self.url, href)
            if any(search(x, url) for x in blacklist):
                continue
            yield url