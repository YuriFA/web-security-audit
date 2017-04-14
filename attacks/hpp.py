from utils import compare, append_url_params, dict_iterate, update_url_params, get_url_query
from client import NotAPage, RedirectedToExternal

PAYLOAD = "HPP_TEST"

def hpp(page, client, log):
    page_content = page.document.contents
    query = get_url_query(page.url)

    for param, value in dict_iterate(query):
        injected_url = update_url_params(page.url, {param: PAYLOAD})
        combining_url = append_url_params(page.url, param, PAYLOAD)
        try:
            injected_content = client.get(injected_url).document.contents
            combining_content = client.get(combining_url).document.contents
        except (NotAPage, RedirectedToExternal) as e:
            continue

        if not compare(page_content, combining_content) \
            and not compare(injected_content, combining_content):
            log('warn', 'hpp', page.url, param)
