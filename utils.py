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

def get_url_host(url):
    # print(url, urlparse(url).netloc)
    return urlparse(url).netloc

def create_form_selector(form):
    selector = 'form'
    for key, value in form.attrs.iteritems():
        selector += '['+key+'="'+value+'"]'

    return selector

def add_url_params(url, params):
    url_parts = list(urlparse(url))
    query = dict(parse_qsl(url_parts[4]))
    print query, params
    query.update(params)

    url_parts[4] = urlencode(query)

    return urlunparse(url_parts)