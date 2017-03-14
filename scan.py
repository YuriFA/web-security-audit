import optparse
import sys
import os
import time

from crawler import Crawler
from attacks import all_attacks
from utils import get_url_host
from client import Client, NotAPage, RedirectedToExternal

VERSION = '0.0.1'

def main(options):
    target_url = options.url

    options.whitelist = set(options.whitelist)

    client = Client()

    if options.auth_data and len(options.auth_data) == 3:
        url, name, passwd = options.auth_data
        form_data = {}

        for arg in (name, passwd):
            name, _, value = arg.partition('=')
            form_data.update({name: value})

        try:
            res_page = client.post_req(url, data=form_data)
        except NotAPage:
            pass
        except RedirectedToExternal:
            pass

    all_pages = Crawler(target_url, client, whitelist=options.whitelist)

    for page in all_pages:
        print 'Scanning: ', page.status_code, page.url
        for attack in all_attacks():
            attack(page, client)


def optlist_callback(option, opt, value, parser):
    setattr(parser.values, option.dest, value.split(','))

if __name__ == "__main__":
    parser = optparse.OptionParser(version=VERSION)
    parser.add_option("-u", "--url", dest="url", help="Target URL (e.g. \"http://www.target.com/page.php?id=1\")")
    parser.add_option("-a", dest="auth_data", help="Enter 3 args URL, fieldname=username, fieldname=password for sending request to log in", nargs=3, metavar="http://www.target.com/?login=true user passwd")
    parser.add_option("-w", "--whitelist", type="string", action='callback', callback=optlist_callback, dest="whitelist", help="Hosts that will not be blocked", metavar="same.target.com, same2.target.com...", default={})
    parser.add_option("--cookie", dest="cookie", help="HTTP Cookie header value")
    parser.add_option("--user-agent", dest="ua", help="HTTP User-Agent header value")
    parser.add_option("--referer", dest="referer", help="HTTP Referer header value")
    parser.add_option("--proxy", dest="proxy", help="HTTP proxy address (e.g. \"http://127.0.0.1:8080\")")
    options, _ = parser.parse_args()

    if options.url:
        try:
            main(options)
        except KeyboardInterrupt:
            print 'Interrupted'
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)
    else:
        parser.print_help()