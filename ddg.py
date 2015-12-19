#!/usr/bin/env python
# ddg.py - Library for querying DuckDuckGo.com
# 
# Copyright (c) 2015 Casey Bartlett <caseytb@bu.edu>
# 
# See LICENSE for terms of usage, modification and redistribution.

from bs4 import BeautifulSoup as bs
from urllib2 import urlopen, URLError
import re

def construct_string(search_string):
    return search_string.replace(" ","+")

class ddg:
    def __init__(self):
        self.html_site = 'http://duckduckgo.com/html/?'
        self.java_site = 'http://duckduckgo.com/?' # doesn't really work..
        self.site = self.html_site 
        self.results = []# text : site 
        self.nresults = 10
        # if json is used the ddg api is calledl
        self.parser = self.soup_parser
    def query(self, query_text, use_json=False, site=""):
        formatted_text = construct_string(query_text)
        query_string = "{target}q={q}".format(target=self.site, q=formatted_text)
        if site:
            query_string += "+site%3A{site}".format(site=site)
        if use_json:
            query_string += "&format=json"
            self.parser = self.json_parser
        self.parser(query_string)
    def json_parser(self):
        pass
    def soup_parser(self,formatted_query):
        try:
            page = urlopen(formatted_query)
        except URLError as e:
            print(e.reason)
        soup = bs(page)
        results = soup.findAll('div', {'class': re.compile('links_main*')})
        for r in results:
            if (self.results):
                break
            self.results.append(r.a['href'])
            print r.a['href']
        if not r:
            print("{} not found".format(formatted_query))

def run():
    # Simple usage
    d = ddg()
    d.query("Paramilitary 2", site="bladehq.com")
    print d.results[0]

if __name__ == '__main__':
    run()

