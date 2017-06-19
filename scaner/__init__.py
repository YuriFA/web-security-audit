# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .crawler import Crawler
from .attacks import all_attacks
from .cms_attacks import attack_cms
from .utils import get_url_host, validate_url, dict_iterate, read_config, check_boolean_option
from .client import Client, NotAPage, RedirectedToExternal
from .app_detect import app_detect
from .logger import Log
from datetime import datetime, timedelta
from timeit import default_timer as timer

import optparse
import sys
import os

VERSION = '1.0.0'

def run(options):
    date_now = datetime.today()
    start_scan = timer()
    cms = None
    target_url = validate_url(options.get('url'))
    additional_pages = []
    options['whitelist'] = set(options.get('whitelist'))

    client = Client()
    log = Log()

    auth_info = options.get('auth')
    if auth_info:
        res_page = website_auth(auth_info, client)
        additional_pages.append(res_page.url)
        print(res_page.url)

    apps = app_detect(target_url, client)
    detected_apps = {}
    if apps:
        print('Используемые технологии:')
        for app, app_types in dict_iterate(apps):
            for app_type in app_types:
                detected_apps.setdefault(app_type, []).append(app)
            if 'CMS' in app_types:
                cms = app
            app_types_string = ", ".join(app_types)
            print('\t{} - {}'.format(app_types_string, app))

    if options.get('page_only'):
        page = client.get(target_url)
        all_pages = [page]
    else:
        all_pages = Crawler(target_url, client, whitelist=options.get('whitelist'), additional_pages=additional_pages)

    try:
        if cms:
            attack_cms(cms, target_url, client, log)
        for page in all_pages:
            print('Проверка страницы: [{}] {}'.format(page.status_code, page.url))
            log.add_url(page.url, color='green')
            # for attack in all_attacks():
            #     attack(page, client, log)


    except KeyboardInterrupt:
        print('Interrupted')
    finally:
        end_scan = timer()
        scan_seconds = round(end_scan - start_scan)
        scan_time = str(timedelta(seconds=scan_seconds))
        audit_info = {
            'date': date_now,
            'url': target_url,
            'host': get_url_host(target_url),
            'scan_time': scan_time,
            'detected_apps': detected_apps,
        }
        log.write_report(options.get('csv_file') or 'audit_{}.csv'.format(get_url_host(target_url)))
        log.write_html_report(options.get('html_file') or 'audit_{}.html'.format(get_url_host(target_url)), audit_info)
        print('Проверено страниц : {}'.format(1 if options.get('page_only') else all_pages.count))

def website_auth(auth_info, client):
    auth_url = auth.get('url')
    auth_data = auth.get('auth_data', {})
    res_page = None
    try:
        res_page = client.post(auth_url, data=auth_data)
    except (NotAPage, RedirectedToExternal) as e:
        print('Error', e)

    return res_page


def auth_option_callback(option, opt, value, parser):
    url, name, passwd = value
    auth_data = {}

    for arg in (name, passwd):
        name, _, value = arg.partition('=')
        auth_data.update({name: value})
    setattr(parser.values, option.dest, {"url": url, "auth_data": auth_data})

def whitelist__option_callback(option, opt, value, parser):
    setattr(parser.values, option.dest, value.split(','))

def main():
    parser = optparse.OptionParser(version=VERSION)
    parser.add_option("-u", "--url", dest="url", help="Target URL (e.g. \"http://www.target.com/page.php?id=1\")", default='')
    parser.add_option("-a", dest="auth", type="string", action='callback', callback=auth_option_callback, help="Enter 3 args URL, fieldname=username, fieldname=password for sending request to log in", nargs=3, metavar="http://www.target.com/?login=true user passwd", default={})
    parser.add_option("-w", "--whitelist", type="string", action='callback', callback=whitelist__option_callback, dest="whitelist", help="Hosts that will not be blocked", metavar="same.target.com, same2.target.com...", default={})
    parser.add_option("--pageonly", action="store_true", dest="page_only", help="Scan this page url only", default=False)
    parser.add_option("--print", action="store_true", dest="direct_print", help="Output in console", default=False)
    parser.add_option("--csv", type="string", dest="csv_file", help="Filename (*.csv) for writing report", metavar="test.csv")
    parser.add_option("--html", type="string", dest="html_file", help="Filename (*.html) for writing report", metavar="test.html")
    parser.add_option("-c", "--config", type="string", dest="config", help="Read the parameters from FILE", metavar="config.json")
    options, _ = parser.parse_args()
    options = options.__dict__

    if options.get('config'):
        options = read_config(options.get('config'))
        options['pageonly'] = check_boolean_option(options.get('pageonly', ''))
        options['print'] = check_boolean_option(options.get('print', ''))
        url = options.get('url', '')

    if options.get('url', ''):
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