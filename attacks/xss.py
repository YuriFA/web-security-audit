from ghost import Ghost, TimeoutError
from utils import create_form_selector, add_url_params
from urlparse import urlparse

browser = Ghost()

XSS_STRING = u'<script>alert("XSS_STRING");</script>'

def xss(page, client):
    print page.cookies
    try:
        with browser.start() as session:
            session.load_cookies(page.cookies)
            for form in page.get_forms():
                method = form.get('action') or 'GET'
                inject = inject_form(form)
                if 1 == 0 and method == 'POST':
                    session_page, extra_resources = session.open(page.url)
                    selector = create_form_selector(form)
                    result, resources = session.fill(selector, dict(inject))
                    response_page, resources = session.call("form", "submit", expect_loading=True)
                    result, resources = session.wait_for_alert(2)
                else:
                    injected_url = add_url_params(page.url, inject)
                    response_page, extra_resources = session.open(injected_url) #, user_agent=useragent)
                    result, resources = session.wait_for_alert(1)

                print result

    except TimeoutError as e:
        print page.url, e
    except Exception as e:
        raise e

def inject_form(form):
    inject = {}
    immutable_types = ['submit','button','hidden','radio', 'checkbox']
    inputs = form.find_all('input')
    textareas = form.find_all('textarea')

    for inpt in inputs:
        name = str(inpt.get('name'))
        value = str(inpt.get('value')) or ''
        print name, value
        if not inpt.get('type') in immutable_types:
            value += XSS_STRING
            inject[name] = value


    for txt in textareas:
        name = str(txt.get('name'))
        value = str(txt.text + XSS_STRING)
        inject[name] = value

    return inject