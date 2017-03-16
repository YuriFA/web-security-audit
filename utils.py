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

def update_url_params(url, params):
    if isinstance(url, ParseResult):
        url_parts = list(url)
    else:
        url_parts = list(urlparse(url))

    query = dict(parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urlencode(query)
    return urlunparse(url_parts)

def replace_url_params(url, replace):
    if isinstance(url, ParseResult):
        url_parts = list(url)
    else:
        url_parts = list(urlparse(url))

    query = {k: replace for k in dict(parse_qsl(url_parts[4]))}
    url_parts[4] = urlencode(query)
    return urlunparse(url_parts)

def request_params(client, url, method, params):
    if method.lower() == POST.lower():
        res_page = client.post(url, data=params)
    else:
        injected_url = update_url_params(url, params)
        res_page = client.get(injected_url)

    return res_page

def modify_parameter(parameters, key, value):
    res = parameters.copy()
    res[key] = value
    return res

def get_form_params(form):
    """get all params from bs4 form"""
    injectable, immutable = {}, {}
    immutable_types = ['submit', 'button', 'hidden']

    for inpt in form.find_all('input'):
        name = str(inpt.get('name') or '')
        if not name:
            continue

        itype = inpt.get('type') or 'text'
        value = inpt.get('value')

        if value and is_ascii(value):
            value = value.encode('utf-8')

        if not value or not itype in immutable_types:
            value = INPUT_TYPE_DICT[itype]

        if itype in immutable_types:
            immutable[name] = value
        else:
            injectable[name] = value

    for txt in form.find_all('textarea'):
        name = str(txt.get('name'))
        value = str(txt.text or INPUT_TYPE_DICT['text'])
        injectable[name] = value

    return injectable, immutable

def is_ascii(s):
     return not all(ord(char) < 128 for char in s)

def is_search_form(form):
    form_id = form.get('id') or ""
    form_class = form.get('class') or ""
    return "search" in form_id.lower() or "search" in form_class.lower()

def compare(x, y):
    return collections.Counter(x) == collections.Counter(y)

def get_url_query(url):
    return dict(parse_qsl(list(urlparse(url))[4]))

def validate_url(url):
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        parsed_url = parsed_url._replace(**{"scheme": "http"})
    return parsed_url.geturl().replace('///', '//')