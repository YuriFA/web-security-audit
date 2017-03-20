from utils import dict_iterate, update_url_params, replace_url_params, get_url_query, modify_parameter
from compat import urlparse
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
    # print("Testing for SQL Error in page {}".format(page.url))

    url = page.url
    query = get_url_query(url)

    for param, value in dict_iterate(query):
        injected_url = update_url_params(page.url, {param: PAYLOAD})
        try:
            res_page = client.get(injected_url)
        except NotAPage:
            continue
        except RedirectedToExternal:
            continue

        check_sql_error(res_page)

    for form in page.get_forms():

        form_parameters = dict(form.get_parameters())
        for param in form_parameters:
            injected_params = modify_parameter(form_parameters, param, PAYLOAD)
            try:
                res_page = form.send(client, injected_params)
                check_sql_error(res_page)
            except NotAPage:
                continue
            except RedirectedToExternal:
                continue

        if urlparse(form.action).query:
            injected_action = replace_url_params(form.action, PAYLOAD)

            try:
                res_page = form.send(client, form_parameters, changed_action=injected_action)
                check_sql_error(res_page)
            except NotAPage:
                continue
            except RedirectedToExternal:
                continue

def check_sql_error(res_page):
    for db, errors in dict_iterate(DBMS_ERRORS):
        for e in errors:
            res = re.findall(e, res_page.html)
            if res:
                print('SQL error ({}) in {}. Error: {}'.format(db, res_page.url, res))