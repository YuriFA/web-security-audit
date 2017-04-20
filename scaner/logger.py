from .utils import remove_url_params

import csv
import os

LEVEL_NAMES = {
    'warn': 'Warning',
    'vuln': 'Vulnerability',
}

ATTACK_TYPES = {
    'xss': 'Cross-Site Scripting (XSS)',
    'xss_file': 'Remote file inclusion XSS',
    'hpp': 'HTTP Parameter Pollution',
    'breach': 'Breach',
    'clickjack': 'Clickjack',
    'cookiescan': 'Implicit Cacheable Cookies',
    'clrf': 'Carriage Return Line Feed',
    'csrf': 'Cross-Site Request Forgery',
    'directory_listing': 'Directory listing',
    'lfi': 'Local File Inclusion',
    'sql_blind': 'SQL Blind',
    'sql_error': 'SQL Error',
    'cms_vuln': 'CMS Vulnerability'
}

REPORTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'reports')

def entry_str(level, type, url, param, injections=None, request=None, message=None):
    if param is None:
        return "{} {} in {}".format(level, type, url)
    else:
        return "{} {} in {} on param {}".format(level, type, url, param)

class Log(object):
    def __init__(self, direct_print=True):
        self.entries = []
        self.direct_print = direct_print

    def __call__(self, level, a_type, url, param=None, injections=None, request=None, message=None):
        assert level in LEVEL_NAMES
        assert a_type in ATTACK_TYPES

        level_name = LEVEL_NAMES[level]
        attack_type = ATTACK_TYPES[a_type]
        url_ = remove_url_params(url)

        entry = {
            'level': level_name,
            'type': attack_type,
            'url': url_,
            'param': param,
            'injections': injections,
            'request': request,
            'message': message
        }

        if not entry in self.entries:
            self.entries.append(entry)
            if self.direct_print:
                print(entry_str(**entry))

    def write_report(self, filename='test.csv'):
        file_path = os.path.join(REPORTS_DIR, filename)
        with open(file_path, 'w') as csvfile:
            fieldnames = ['level', 'type', 'url', 'param']
            writer = csv.DictWriter(csvfile, extrasaction='ignore', fieldnames=fieldnames,
                                    delimiter=';', lineterminator='\n')

            writer.writeheader()
            writer.writerows(self.entries)
