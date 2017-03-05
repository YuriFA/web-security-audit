import optparse
import sys
import os

from ghost import Ghost
from crawler import Crawler

VERSION = '0.0.1'

def main(options):
    target_url = options.url
    all_pages = Crawler(target_url)

    for page in all_pages:
        print page.status_code, page.url

if __name__ == "__main__":
    parser = optparse.OptionParser(version=VERSION)
    parser.add_option("-u", "--url", dest="url", help="Target URL (e.g. \"http://www.target.com/page.php?id=1\")")
    parser.add_option("--data", dest="data", help="POST data (e.g. \"query=test\")")
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
        # init_options(options.proxy, options.cookie, options.ua, options.referer)
        # result = scan_page(options.url if options.url.startswith("http") else "http://%s" % options.url, options.data)
        # print "\nscan results: %s vulnerabilities found" % ("possible" if result else "no")
    else:
        parser.print_help()