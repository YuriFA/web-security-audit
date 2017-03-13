from utils import add_url_params, change_url_params, get_url_host, INPUT_TYPE_DICT, POST, GET
from urlparse import urlparse, urljoin
from client import NotAPage, RedirectedToExternal

import re
import time

PAYLOAD = "'"
DBMS_ERRORS = {
    "MySQL": (r"SQL syntax.*MySQL", r"Warning.*mysql_.*", r"valid MySQL result", r"MySqlClient\."),
    "PostgreSQL": (r"PostgreSQL.*ERROR", r"Warning.*\Wpg_.*", r"valid PostgreSQL result", r"Npgsql\."),
    "Microsoft SQL Server": (r"Driver.* SQL[\-\_\ ]*Server", r"OLE DB.* SQL Server", r"(\W|\A)SQL Server.*Driver", r"Warning.*mssql_.*", r"(\W|\A)SQL Server.*[0-9a-fA-F]{8}", r"(?s)Exception.*\WSystem\.Data\.SqlClient\.", r"(?s)Exception.*\WRoadhouse\.Cms\."),
    "Microsoft Access": (r"Microsoft Access Driver", r"JET Database Engine", r"Access Database Engine"),
    "Oracle": (r"\bORA-[0-9][0-9][0-9][0-9]", r"Oracle error", r"Oracle.*Driver", r"Warning.*\Woci_.*", r"Warning.*\Wora_.*"),
    "IBM DB2": (r"CLI Driver.*DB2", r"DB2 SQL error", r"\bdb2_\w+\("),
    "SQLite": (r"SQLite/JDBCDriver", r"SQLite.Exception", r"System.Data.SQLite.SQLiteException", r"Warning.*sqlite_.*", r"Warning.*SQLite3::", r"\[SQLITE_ERROR\]"),
    "Sybase": (r"(?i)Warning.*sybase.*", r"Sybase message", r"Sybase.*Server message.*"),
}

def sql_error(page, client):
    print "Scanning SQL Error in page {}".format(page.url)
    for form in page.get_forms():
        report = {}
        action = urljoin(page.url, form.get('action'))

        method = form.get('method') or GET

        injected_action = None
        if urlparse(action).query:
            injected_action = change_url_params(action, PAYLOAD)

        inject = inject_form(form)

        try:
            for actn in (action, injected_action):
                if not actn or get_url_host(page.url) != get_url_host(actn):
                    continue
                if method.lower() == POST.lower():
                    res_page = client.post_req(actn, data=inject)
                else:
                    injected_url = add_url_params(actn, inject)
                    res_page = client.get_req(injected_url)

                for db, errors in DBMS_ERRORS.iteritems():
                    for e in errors:
                        res = re.findall(e, res_page.html)
                        if res:
                            print 'SQL error ({}) in {}. Error: {}'.format(db, page.url, res)

        except NotAPage:
            continue
        except RedirectedToExternal:
            continue

def inject_form(form):
    injected_form, immutable = {}, {}
    immutable_types = ['submit', 'button', 'hidden']
    inputs = form.find_all('input')
    textareas = form.find_all('textarea')

    for inpt in inputs:
        name = str(inpt.get('name') or '')
        if not name:
            continue
        itype = inpt.get('type')
        if itype in immutable_types:
            immutable[name] = inpt.get('value') or INPUT_TYPE_DICT[itype]
        else:
            injected_form[name] = PAYLOAD

    for txt in textareas:
        name = str(txt.get('name'))
        injected_form[name] = PAYLOAD

    injected_form.update(immutable)
    return injected_form