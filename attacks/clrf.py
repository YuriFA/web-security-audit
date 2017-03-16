from utils import is_ascii, request_params, modify_parameter, update_url_params, get_url_query, INPUT_TYPE_DICT, GET, POST
from urlparse import urljoin
from client import NotAPage, RedirectedToExternal

BODY = u'o'
CLRF_SEQUENCE = (
    u"Content-Type: text/html\r\n" +
    u"Content-Length: %d\r\n\r\n" % len(BODY))
ATTACK_SEQUENCE = CLRF_SEQUENCE + BODY

def clrf(page, client):
    print "Testing for CLRF in page {}".format(page.url)

    attack_url(page.url, client)

    for form in page.get_forms():
        report = {}
        action = urljoin(page.url, form.get('action'))
        method = form.get('method') or GET

        parameters = dict(get_form_parameters(form))
        for parameter in parameters:
            injected_parameters = modify_parameter(parameters, parameter, ATTACK_SEQUENCE)

            try:
                res_page = request_params(client, action, method, injected_parameters)
                check_clrf(res_page)

            except NotAPage:
                continue
            except RedirectedToExternal:
                continue


def attack_url(url, client):
    query = get_url_query(url)
    report = {}

    for param, value in query.iteritems():
        successed = []
        injected_url = update_url_params(url, {param: ATTACK_SEQUENCE})

        try:
            res_page = client.get(injected_url)
            check_clrf(res_page)
        except NotAPage:
            continue
        except RedirectedToExternal:
            continue

def check_clrf(res_page):
    if res_page.headers.get('Content-Length') == str(len(BODY)):
        print 'CLRF injection in form {}'.format(action)

def get_form_parameters(form, filter_type=None):
    for inpt in form.find_all('input'):
        name = str(inpt.get('name') or '')
        if not name:
            continue

        itype = inpt.get('type') or 'text'
        value = inpt.get('value')

        if value and is_ascii(value):
            value = value.encode('utf-8')

        if not value:
            value = INPUT_TYPE_DICT[itype]

        if not filter_type or filter_type and itype != filter_type:
            yield name, value

    for txt in form.find_all('textarea'):
        name = str(txt.get('name'))
        value = str(txt.text or INPUT_TYPE_DICT['text'])

        yield name, value