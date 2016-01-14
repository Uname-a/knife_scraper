#!/usr/bin/env python
# bhq_query.py - module for sopel to query blade head quarters site for knife data
# 
# Copyright (c) 2015,2016 Casey Bartlett <caseytb@bu.edu>
# 
# See LICENSE for terms of usage, modification and redistribution.

from sopel import  *
from random import randint

@module.commands('cf','catfact')
@module.rate(10)
def knife(bot, trigger):
    """ Tell someone a wonderful fact about cats """
    f = open("/home/knifebot/.sopel/knifeclub_modules/cat_facts.txt")
    fact_list = f.readlines()
    max_fact = len(fact_list)
    fact_num = randint(0,max_fact-1)
    bot.say('{}'.format(fact_list[fact_num].strip()))
