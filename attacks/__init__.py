from xss import xss
from sql_error import sql_error
from sql_blind import sql_blind
from csrf import csrf
from clrf import clrf
from directory_listing import directory_listing

def all_attacks():
    return [xss, sql_error, sql_blind, csrf, clrf, directory_listing]
    # return [directory_listing]