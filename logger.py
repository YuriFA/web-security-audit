import csv

LEVEL_NAMES = {
    'warn': 'Warning',
    'vuln': 'Vulnerability',
}

ATTACK_TYPES = {
    'xss': 'Cross-Site Scripting',
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
}

def entry_str(level, type, url, param, injections=None, request=None):
    if param is None:
        return "{} {} in {}".format(level, type, url)
    else:
        return "{} {} in {} on param {}".format(level, type, url, param)

class Log(object):
    def __init__(self, direct_print=True):
        self.entries = []
        self.direct_print = direct_print

    def __call__(self, level, a_type, url, param=None, injections=None, request=None):
        assert level in LEVEL_NAMES
        assert a_type in ATTACK_TYPES

        level_name = LEVEL_NAMES[level]
        attack_type = ATTACK_TYPES[a_type]

        entry = {'level': level_name, 'type': attack_type, 'url': url, 'param': param, 'injections': injections, 'request': request}
        self.entries.append(entry)

        if self.direct_print:
            print(entry_str(**entry))

    def write_report(self, filename='reports/test.csv'):
        with open(filename, 'wb') as csvfile:
            fieldnames = ['level', 'type', 'url', 'param']
            writer = csv.DictWriter(csvfile, extrasaction='ignore', fieldnames=fieldnames, delimiter=';')

            writer.writeheader()
            writer.writerows(self.entries)
