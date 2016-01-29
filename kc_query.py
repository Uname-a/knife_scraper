#!/usr/bin/env python
# kc_query.py - module for sopel to query knifecenter.com for pricing data
# 
# Copyright (c) 2016 Casey Bartlett <caseytb@bu.edu>
# 
# See LICENSE for terms of usage, modification and redistribution.

from sopel import  *
from ddg import ddg
from extract_blade_info import query_kc_knife, KnifeFormatter, replaceDictKeys

@module.commands('kcknife')
def knife(bot, trigger):
    """
    Queries a knife center knife
    """
    query = trigger.group(2)
    d = ddg()
    d.query(query, site="knifecenter.com")
    #use the first result
    if not d.results:
        bot.reply("I couldn't find anything with the search term {}".format(query))
        return
    url = d.results[0]
    knife = query_kc_knife(url)
    if not knife:
        bot.reply('Sorry I didn\'t find anything I could parse, but I did find this {url}'.format(url=url))
    else:
        # need to handle "product type" better ( search again if not knife )
        if knife["Product Type"] == "Knife":
            d = replaceDictKeys(BHQNAME_TO_DBNAME,knife)
            kf = KnifeFormatter()
            results_string = kf.formattedKnife(d)
            bot.reply(results_string)
        else:
            d = replaceDictKeys(BHQNAME_TO_DBNAME,knife)
            kf = KnifeFormatter()
            results_string = kf.formattedKnife(d)
            bot.reply("I know this isn't a knife, but its what i found:" + results_string)

