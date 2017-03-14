from xss import xss
from sql_error import sql_error
from sql_blind import sql_blind

def all_attacks():
    return [xss, sql_error, sql_blind]