from urlparse import urlparse, urljoin, parse_qsl
import os.path

url = 'http://testphp.vulnweb.com/Mod_Rewrite_Shop/Details/network-attached-storage-dlink/1/index.php'

parsed = urlparse(url)
print parsed
path = parsed.path

while os.path.dirname(path) != '/':
    path = os.path.dirname(path)
    print path