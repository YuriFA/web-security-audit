#!/usr/bin/python
from utils import get_url_host
from client import Client, NotAPage, RedirectedToExternal
from collections import deque
from re import search

class Crawler(object):
    def __init__(self, target, whitelist=None, blacklist=set(), client=None):
        self.target = target

        if whitelist is None:
            self.whitelist = { get_url_host(target) }
        else:
            self.whitelist = whitelist

        self.blacklist = blacklist

        if client is None:
            self.client = Client()
        else:
            self.client = client

        self.to_visit_links = deque()
        self.visited_links  = set()
        self.count = 0 # Simple counter for debug

    def __iter__(self):
        self.to_visit_links.append(self.target)

        while self.to_visit_links:
            url = self.to_visit_links.pop()

            if not get_url_host(url) in self.whitelist:
                continue

            if any(search(x, url) for x in self.blacklist):
                continue

            url_without_hashbang, _, _ = url.partition("#")
            if url_without_hashbang in self.visited_links:
                continue

            self.visited_links.add(url_without_hashbang)
            try:
                page = self.client.get_page(url)
            except NotAPage:
                continue
            except RedirectedToExternal:
                continue

            self.count += 1

            yield page
            self.to_visit_links.extend(page.get_links())

if __name__ == "__main__":
    target_url = "http://testphp.vulnweb.com/"
    all_pages = Crawler(target_url)

    for page in all_pages:
        print(page.url)

    print(all_pages.count)
