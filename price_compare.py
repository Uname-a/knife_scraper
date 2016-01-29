#!/usr/bin/env python
# kc_query.py - module for sopel to query knifecenter.com for pricing data
#
# Copyright (c) 2016 Casey Bartlett <caseytb@bu.edu>
# 
# See LICENSE for terms of usage, modification and redistribution.


from sopel import  *
from ddg import ddg
from extract_blade_info import query_kc_knife, query_bhq_knife,  replaceDictKeys
from kc_inventory_items import KCNAME_TO_DBNAME

class query_attributes:
    def __init__(self, site_name, query_fcn, DB_CONVERTER):
        self.site = site_name
        self.fcn = query_fcn
        self.DBC = DB_CONVERTER
        self.price = 1000000
        self.url = ""
        self.knife = []

@module.commands('pcmp')
def knife(bot, trigger):
    """
    Price compare between all available query engines
    """
    query = trigger.group(2)
    d = ddg()
    sites = [ query_attributes("knifecenter.com",
                query_kc_knife,
                KCNAME_TO_DBNAME),
              query_attributes("bladehq.com",
                query_bhq_knife,
                KCNAME_TO_DBNAME)]
    for qa in sites:
        s = qa.site
        d.query(query, site=s)
        if not d.results:
            bot.reply("I couldn't find anything with the search term {} at {}".format(query,s))
            return
        else:
           qa.url = d.results[0]
    comp_string  = ""
    for qa in sites:
        if qa.url:
            knife = qa.query_fcn(v)
            d = replaceDictKeys(qa.DBC,knife)
            qa.price = d["Price"]
            comp_string += "[{site}:{price}] ".format(site=d.site, price = qa.price)

    if(comp_string):
        bot.say(comp_string)

