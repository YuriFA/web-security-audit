from utils import is_ascii, request_params, is_search_form, compare, INPUT_TYPE_DICT, GET, POST
from urlparse import urljoin
from client import NotAPage, RedirectedToExternal

def csrf(page, client):
    print "Testing for CSRF in page {}".format(page.url)

    for form in page.get_forms():
        if is_search_form(form):
            continue

        action = urljoin(page.url, form.get('action'))
        method = form.get('method') or GET

        valid_params = dict(fill_entries(form))
        broken_params = dict(fill_entries(form, "hidden"))

        try:
            valid_res = request_params(client, action, method, valid_params)
            broken_res = request_params(client, action, method, broken_params)

            if broken_res.status_code == 200 \
                and compare(list(valid_res.document.stripped_strings), list(broken_res.document.stripped_strings)):

                print 'HTML form without CSRF protection {}'.format(action)

        except NotAPage:
            continue
        except RedirectedToExternal:
            continue

def fill_entries(form, filter_type=None):
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
