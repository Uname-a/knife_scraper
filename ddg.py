#!/usr/bin/env python
# ddg.py - Library for querying from DuckDuckGo.com
# 
# Copyright (c) 2015,2016 Casey Bartlett <caseytb@bu.edu>
# 
# See LICENSE for terms of usage, modification and redistribution.

from bs4 import BeautifulSoup as bs
from urllib.request import urlopen, URLError
from difflib import SequenceMatcher
import re

def construct_string(search_string):
    good_html_string = search_string.replace("/","")
    return good_html_string.replace(" ","+")

def get_best_match(candidates, query_string):
    max_score = 0
    best_candidate = ""
    for c in candidates:
        s = SequenceMatcher(None, query_string, c )
        score = s.ratio()
        if score > max_score:
            max_score = score
            best_candidate = c
    if best_candidate:
        return best_candidate
    else:
        return candidates[0]

class ddg:
    def __init__(self):
        self.html_site = 'http://duckduckgo.com/html/?'
        self.java_site = 'http://duckduckgo.com/?' # without html use json - but page uses js
        self.site = self.html_site 
        self.results = []# text : site 
        self.depth_limit = 1
        self.current_depth = 0
        self.last_url = ""
        # if json is used the ddg api is called
        self.parser = self.soup_parser
    def query(self, query_text, use_json=False, site=""):
        if not query_text:
            return
        formatted_text = construct_string(query_text)
        query_string = "{target}q={q}".format(target=self.site, q=formatted_text)
        if site:
            query_string = "{target}q=site%3A{site}+{q}".format(target=self.site, site=site, q=formatted_text)
        if use_json:
            query_string += "&format=json"
            self.parser = self.json_parser
        self.parser(query_string)
    def bhq_safe_query(self, query_text, use_json=False, site=""):
        self.query(query_text, use_json, site)
        # check if "cat" is in the returned url
        if not self.results:
            return
        page_url = self.results[0]

        if "/cat--" in page_url and self.last_url != page_url:
            if self.current_depth < self.depth_limit:
                self.last_url = page_url
                try:
                    page = urlopen("{url}".format(url=page_url))
                except URLError as e:
                    print(e.reason+ " " + page_url)
                soup = bs(page)
                meta = soup.find("meta",{"name":"keywords"})
                bhq_items = meta["content"].split(",")
                best_bhq_match = get_best_match(bhq_items,query_text)
                self.current_depth+=1
                self.bhq_safe_query(best_bhq_match, use_json, site)
            else:
                self.results = []

    def json_parser(self):
        pass
    def soup_parser(self,formatted_query):
        self.results = []
        try:
            page = urlopen(formatted_query)
        except URLError as e:
            print(e.reason + " " + formatted_query)
        soup = bs(page)
        results = soup.findAll('div', {'class': re.compile('links_main*')})
        for r in results:
            if (self.results):
                break
            if r.a:
                self.results.append(r.a['href'])
        if not r:
            print("{} not found".format(formatted_query))
def safe_run():
    d = ddg()
    d.bhq_safe_query("griptillian", site="bladehq.com")
    print(d.results[0])

def run():
    # Simple usage
    d = ddg()
    d.query("Paramilitary 2", site="bladehq.com")
    print(d.results[0])

if __name__ == '__main__':
    run()

