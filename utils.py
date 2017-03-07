from urlparse import urlparse, urlunparse, parse_qsl
from urllib import urlencode

NOT_A_PAGE_CONTENT_TYPES = frozenset([
    'text/plain',
    'text/x-python',
    'image/gif',
    'image/jpeg',
    'image/png',
    'image/svg+xml',
])

INPUT_TYPE_DICT = {
    "text": "abcdefgh",
    "email": "ex@amp.le",
    "password": "abcd1234",
    "checkbox": "true",
    "radio": "1",
    "datetime": "1990-12-31T23:59:60Z",
    "datetime-local":
    "1985-04-12T23:20:50.52",
    "date": "1996-12-19",
    "month": "1996-12",
    "time": "13:37:00",
    "week": "1996-W16",
    "number": "123456",
    "range": "1.23",
    "url": "http://localhost/",
    "search": "query",
    "tel": "012345678",
    "color": "#FFFFFF",
    "hidden": "Secret.",
    "submit": ""
}

def get_url_host(url):
    return urlparse(url).netloc

def create_form_selector(form):
    selector = 'form'
    for key, value in form.attrs.iteritems():
        selector += '['+key+'="'+value+'"]'

    return selector

def add_url_params(url, params):
    url_parts = list(urlparse(url))
    query = dict(parse_qsl(url_parts[4]))
    query.update(params)

    url_parts[4] = urlencode(query)

    return urlunparse(url_parts)