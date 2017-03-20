# -*- coding: utf-8 -*-

"""
This module handles import compatibility issues between Python 2 and
Python 3.
"""

import sys

# -------
# Pythons
# -------

# Syntax sugar.
_ver = sys.version_info

#: Python 2.x?
is_py2 = (_ver[0] == 2)

#: Python 3.x?
is_py3 = (_ver[0] == 3)

# try:
#     import simplejson as json
# except (ImportError, SyntaxError):
#     # simplejson does not support Python 3.2, it throws a SyntaxError
#     # because of u'...' Unicode literals.
#     import json

# ---------
# Specifics
# ---------

if is_py2:
    from urllib import urlencode
    from urlparse import urlparse, urlunparse, urljoin, parse_qsl, ParseResult
    from cookielib import CookieJar

elif is_py3:
    from urllib.parse import urlparse, urlunparse, urljoin, urlencode, parse_qsl, ParseResult
    from http.cookiejar import CookieJar