import requests
import sys

from cookielib import CookieJar
from page import Page
from utils import NOT_A_PAGE_CONTENT_TYPES
from urlparse import urlparse


class NotAPage(Exception):
    """ The content at the URL in question is not a webpage, but something
    static (image, text, etc.) """

class RedirectedToExternal(Exception):
    """ Response return 3** code and redirected to external link """

class Client(object):
    def __init__(self, headers=None):
        self.headers = headers
        self.cookie_jar = CookieJar()


    def get_page(self, url):
        try:
            r = requests.get(url, headers=self.headers, cookies=self.cookie_jar)
            # print r.status_code
        except requests.exceptions.HTTPError as error:
            print(error)
        except requests.exceptions.RequestException as error:
            print(error)
            sys.exit(1)

        if not isinstance(r, requests.Response) or r.headers.get('content-type') in NOT_A_PAGE_CONTENT_TYPES:
            raise NotAPage()

        if r.history and urlparse(r.url).netloc != urlparse(url).netloc:
            raise RedirectedToExternal()

        return Page(r)