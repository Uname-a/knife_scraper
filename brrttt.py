#!/usr/bin/env python
# bhq_query.py - module for sopel to query blade head quarters site for knife data
# 
# Copyright (c) 2016 Casey Bartlett <caseytb@bu.edu>
# 
# See LICENSE for terms of usage, modification and redistribution.

from sopel import  *
import random
from itertools import repeat, imap

def rand_cap(c):
   if random.randint(0, 1):
       return c.upper()
   return c.lower()

@module.commands('a10')
@module.rule('(a).*(10)')
@module.rule('.*[Bb]+[Rr]+[Tt]+.*')
def knife(bot, trigger):
   bot.say(formatting.color("bbb"*random.randint(1,3),fg=formatting.colors.RED) +\
      formatting.color(rand_cap("r")*random.randint(10,24),fg=formatting.colors.WHITE) +\
      formatting.color("t"*random.randint(4,15),fg=formatting.colors.BLUE))
