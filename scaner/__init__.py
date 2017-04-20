from .crawler import Crawler
from .attacks import all_attacks
from .cms_attacks import attack_cms
from .utils import get_url_host, validate_url, print_progress, dict_iterate
from .client import Client, NotAPage, RedirectedToExternal
from .app_detect import app_detect
from .logger import Log

import optparse
import sys
import os

VERSION = '0.0.1'

def run(options):
    cms = None
    target_url = validate_url(options.url)

    options.whitelist = set(options.whitelist)

    client = Client()
    # log = Log(direct_print=options.direct_print)
    log = Log()

    if options.auth_data and len(options.auth_data) == 3:
        url, name, passwd = options.auth_data
        form_data = {}

        for arg in (name, passwd):
            name, _, value = arg.partition('=')
            form_data.update({name: value})

        try:
            res_page = client.post(url, data=form_data)
        except (NotAPage, RedirectedToExternal) as e:
            print(e)

    apps = app_detect(target_url, client)
    if apps:
        print('Detected technologies')
        for app, app_types in dict_iterate(apps):
            print(app_types)
            if 'CMS' in app_types:
                cms = app
            print('{} - {}'.format(app_types, app))

    if options.page_only:
        page = client.get(target_url)
        all_pages = [page]
    else:
        all_pages = Crawler(target_url, client, whitelist=options.whitelist)

    # i = 0
    # l = len(all_pages)

    try:
        if cms:
            attack_cms(cms, target_url, client, log)
        # print_progress(i, l, prefix='Progress:', suffix='Complete', length=50)
        for page in all_pages:
            print('Scanning: [{}] {}'.format(page.status_code, page.url))
            for attack in all_attacks():
                attack(page, client, log)
            # i+=1
            # print_progress(i, l, prefix='Progress:', suffix='Complete', length=50)


    except KeyboardInterrupt:
        print('Interrupted')
    finally:
        log.write_report(options.csv_file or 'test_{}.csv'.format(get_url_host(target_url)))
        print('1' if options.page_only else all_pages.count)

def optlist_callback(option, opt, value, parser):
    setattr(parser.values, option.dest, value.split(','))

def main():
    parser = optparse.OptionParser(version=VERSION)
    parser.add_option("-u", "--url", dest="url", help="Target URL (e.g. \"http://www.target.com/page.php?id=1\")")
    parser.add_option("-a", dest="auth_data", help="Enter 3 args URL, fieldname=username, fieldname=password for sending request to log in", nargs=3, metavar="http://www.target.com/?login=true user passwd")
    parser.add_option("-w", "--whitelist", type="string", action='callback', callback=optlist_callback, dest="whitelist", help="Hosts that will not be blocked", metavar="same.target.com, same2.target.com...", default={})
    parser.add_option("--pageonly", action="store_true", dest="page_only", help="Scan this page url only", default=False)
    parser.add_option("--print", action="store_true", dest="direct_print", help="Output in console", default=False)
    parser.add_option("--csv", type="string", dest="csv_file", help="Filename (*.csv) for writing report", metavar="test.csv")
    options, _ = parser.parse_args()

    if options.url:
        try:
            run(options)
        except KeyboardInterrupt:
            print('Interrupted')
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)
    else:
        parser.print_help()