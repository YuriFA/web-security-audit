from utils import compare
from client import NotAPage, RedirectedToExternal

def csrf(page, client):
    print "Testing for CSRF in page {}".format(page.url)

    for form in page.get_forms():
        if form.is_search_form:
            continue

        valid_params = dict(form.get_parameters())
        broken_params = dict(form.get_parameters("hidden"))

        try:
            valid_res = form.send(client, valid_params)
            broken_res = form.send(client, broken_params)

            if broken_res.status_code == 200 \
                and compare(list(valid_res.document.stripped_strings), list(broken_res.document.stripped_strings)):

                print 'HTML form without CSRF protection {}'.format(form.action)

        except NotAPage:
            continue
        except RedirectedToExternal:
            continue