from urlparse import urlparse, urlunparse, parse_qsl, ParseResult
from urllib import urlencode

import collections

POST, GET = 'POST', 'GET'

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

SCRIPTABLE_ATTRS = (
    'onblur',
    'onchange',
    'onclick',
    'ondblclick',
    'onfocus',
    'onkeydown',
    'onkeypress',
    'onkeyup',
    'onload',
    'onmousedown',
    'onmousemove',
    'onmouseout',
    'onmouseover',
    'onmouseup',
    'onreset',
    'onselect',
    'onsubmit',
    'onunload'
)

def get_url_host(url):
    return urlparse(url).netloc

def create_form_selector(form):
    selector = 'form'
    for key, value in form.attrs.iteritems():
        selector += '['+key+'="'+value+'"]'

    return selector

def add_url_params(url, params):
    if isinstance(url, ParseResult):
        url_parts = list(url)
    else:
        url_parts = list(urlparse(url))

    query = dict(parse_qsl(url_parts[4]))
    query.update(params)

    url_parts[4] = urlencode(query)

    return urlunparse(url_parts)

def change_url_params(url, replace):
    if isinstance(url, ParseResult):
        url_parts = list(url)
    else:
        url_parts = list(urlparse(url))

    query = dict(parse_qsl(url_parts[4]))

    query = {k: replace for k in query}

    url_parts[4] = urlencode(query)

    return urlunparse(url_parts)


def get_form_params(form):
    """get all params from bs4 form"""
    injectable, immutable = {}, {}
    immutable_types = ['submit', 'button', 'hidden']
    inputs = form.find_all('input')
    textareas = form.find_all('textarea')
    for inpt in inputs:
        name = str(inpt.get('name') or '')
        if not name:
            continue
        itype = inpt.get('type') or 'text'
        value = inpt.get('value')
        if not value or not itype in immutable_types and isAscii(value):
            value = INPUT_TYPE_DICT[itype]

        if itype in immutable_types:
            immutable[name] = value
        else:
            injectable[name] = value

    for txt in textareas:
        name = str(txt.get('name'))
        value = str(txt.text or INPUT_TYPE_DICT['text'])
        injectable[name] = value

    return injectable, immutable

def isAscii(s):
     return not all(ord(char) < 128 for char in s)

def compare(x, y):
    return collections.Counter(x) == collections.Counter(y)