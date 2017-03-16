from bs4 import BeautifulSoup
from urlparse import urljoin, parse_qsl
from form import Form

import re

class Page(object):
    def __init__(self, response):
        assert hasattr(response, 'request')
        self.request = response.request
        self.html = response.text
        self.headers = response.headers
        self.cookies = response.cookies
        self.status_code = response.status_code
        self.document = BeautifulSoup(self.html, 'lxml')#'html.parser')
        self.response = response

    @property
    def url(self):
        return self.request.url

    @property
    def url_parameters(self):
        _, _, url = self.url.partition("?")
        return parse_qsl(url)

    def get_forms(self, blacklist=[]):
        """ Generator for all forms on the page. """
        for form in self.document.find_all('form'):
            form_obj = Form(self.url, form)
            if any(search(x, form.get(action)) for x in blacklist):
                continue

            yield form_obj

    def get_links(self, blacklist=[]):
        """ Generator for all links on the page. """
        for ref in [re.split("url=", m.get('content'), flags=re.IGNORECASE)[-1].strip("'") for m in self.document.find_all(attrs={'http-equiv': 'refresh'})]:
            url = urljoin(self.url, ref)
            if any(search(x, url) for x in blacklist):
                continue
            yield url

        for href in [h.get('href') for h in self.document.find_all('a')]:
            url = urljoin(self.url, href)
            if any(search(x, url) for x in blacklist):
                continue
            yield url