from ..utils import compare
from ..client import NotAPage, RedirectedToExternal

def csrf(page, client, log):
    for form in page.get_forms():
        if form.is_search_form:
            continue

        valid_params = dict(form.get_parameters())
        broken_params = dict(form.get_parameters("hidden"))

        try:
            valid_res = form.send(client, valid_params)
            broken_res = form.send(client, broken_params)
        except (NotAPage, RedirectedToExternal) as e:
            continue

        if broken_res.status_code == 200 \
            and compare(list(valid_res.document.stripped_strings), list(broken_res.document.stripped_strings)):

            log('warn', 'csrf', form.action)

