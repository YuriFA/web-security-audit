from collections import deque

import re
import json
import six

APPS_FILE = 'apps.json'

def app_detect(url, client):
    detected = {}
    try:
        page = client.get(url)
    except (NotAPage, RedirectedToExternal) as e:
        print(e)

    with open(APPS_FILE) as cms_file:
        data = json.load(cms_file)

    all_cats = data['categories']
    apps = data['apps']

    for app in apps:
        for t in apps[app]:
            scan_func = type_switch(t)
            if hasattr(scan_func, '__call__'):
                res = scan_func(page, apps[app][t])
                if res:
                    detected.update({app: get_categories(apps.get(app, None), all_cats)})

                    implies = apps[app].get('implies', None)
                    if implies:
                        if isinstance(implies, six.string_types):
                            implies = [ implies ]

                        for i in implies:
                            if i not in detected:
                                detected.update({i: get_categories(apps.get(i, None), all_cats)})

    return detected

def get_categories(app, all_cats):
    if app:
        cats = app.get('cats', [])
        return [all_cats[c]['name'] for c in cats]

def type_switch(t):
    return {
        'url': scan_url,
        'html': scan_html,
        'script': scan_script,
        'meta': scan_meta,
        'headers': scan_headers
    }.get(t, None)

def scan_url(page, patterns):
    # print('url', patterns)
    for pattern in parse(patterns):
        if pattern['regex'].findall(page.url):
            return True

    return False

def scan_html(page, patterns):
    # print('html', patterns)
    for pattern in parse(patterns):
        if pattern['regex'].findall(page.html):
            return True

    return False

def scan_script(page, patterns):
    # print('script', patterns)
    for script in page.document.find_all('script', attrs={'src': True}):
        for pattern in parse(patterns):
            if pattern['regex'].findall(str(script)):
                return True

    return False

def scan_meta(page, patterns):
    # print('meta', patterns)
    for meta_tag in page.document.find_all('meta'):
        for meta_name in patterns:
            if meta_name in (meta_tag.get('name', ''), meta_tag.get('property', '')):
                for pattern in parse(patterns[meta_name]):
                    if pattern['regex'].findall(str(meta_tag.get('content', '').encode('utf-8'))):
                        return True

    return False

def scan_headers(page, patterns):
    # print('headers', patterns)
    headers = dict((k.lower(), v) for k, v in page.headers.iteritems())
    for header in patterns:
        for pattern in parse(patterns[header]):
            cur_header = headers.get(header.lower(), None)
            if isinstance(cur_header, six.string_types) and pattern['regex'].findall(cur_header):
                return True

    return False

def parse(patterns):
    parsed = []

    if isinstance(patterns, six.string_types):
        patterns = [ patterns ]

    for pattern in patterns:
        attrs = {}

        for i, attr in enumerate(pattern.split('\\;')):
            if i:
                attr = attr.split(':')

                if len(attr) > 1:
                    attrs[attr.pop(0)] = ':'.join(attr)
            else:
                attrs['string'] = attr

                try:
                    attrs['regex'] = re.compile(attr.replace('/', '\/'))
                except Exception as e:
                    attrs['regex'] = re.compile('')
                    print(e, attr)

        parsed.append(attrs)

    return parsed
