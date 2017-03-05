from urlparse import urlparse

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