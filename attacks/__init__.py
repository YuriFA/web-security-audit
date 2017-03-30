from .xss import xss
from .sql_error import sql_error
from .sql_blind import sql_blind
from .csrf import csrf
from .clrf import clrf
from .directory_listing import directory_listing
from .breach import breach
from .clickjack import clickjack
from .cookiescan import cookiescan
from .lfi import lfi

def all_attacks():
    return [xss, sql_error, sql_blind, csrf, clrf, lfi, directory_listing, breach, clickjack, cookiescan]
    # return [lfi]