from ghost import Ghost, TimeoutError
from utils import create_form_selector, add_url_params, INPUT_TYPE_DICT
from urlparse import urlparse

browser = Ghost()

POST, GET = 'POST', 'GET'

XSS_STRING = u'<script>alert("XSS_STRING");</script>'


def xss(page, client):
    try:
        with browser.start() as session:
            session.load_cookies(page.cookies)
            for form in page.get_forms():
                method = form.get('method') or GET
                print form.get('action')
                injectable, immutable = get_form_params(form)

                for param in injectable.keys():
                    inject = inject_param(injectable, param)
                    inject.update(immutable)

                    if method.lower() == POST.lower():
                        session_page, extra_resources = session.open(page.url)
                        selector = create_form_selector(form)
                        fill_result, _ = session.fill(selector, dict(inject))
                        response_page, _ = session.call(selector, "submit", expect_loading=True)
                        result, _ = session.wait_for_alert(3)
                    else:
                        injected_url = add_url_params(page.url, inject)
                        response_page, extra_resources = session.open(injected_url) #, user_agent=useragent)
                        result, _ = session.wait_for_alert(1)

                    print result

    except TimeoutError as e:
        print page.url, e
    except Exception as e:
        raise e

def inject_param(parameters, param):
    injected = parameters
    injected[param] += XSS_STRING
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