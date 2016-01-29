#!/usr/bin/env python
# bhq_query.py - module for sopel to query blade head quarters site for knife data
# 
# Copyright (c) 2016 Casey Bartlett <caseytb@bu.edu>
# 
# See LICENSE for terms of usage, modification and redistribution.

from sopel import  *
import random
from itertools import repeat, imap

def random_cap(c):
   temp = random.randint(0,2)
   if temp == 0:
        c = formatting.color(c,fg=formatting.colors.RED)
   elif  temp == 1:
        c = formatting.color(c,fg=formatting.colors.BLUE)
   elif temp == 2:
        c = formatting.color(c,fg=formatting.colors.WHITE)
   if random.randint(0, 1):
       return c.upper()
   return c.lower()

def random_chars(s):
   new_s = []
   for c in s:
       new_s.extend(imap(random_cap, repeat(c, random.randint(1, 10))))
   return ''.join(new_s)

@module.commands('a10')
@module.rule('.*\s[aA](\-)?10\W*')
@module.rule('^[aA](\-)?10\W*')
@module.rule('.*\s[Bb]+[Rr]+[Tt]+\W*')
@module.rule('^[Bb]+[Rr]+[Tt]+\W*')
def knife(bot, trigger):
        bot.say(random_chars('bbrrrrtt!'))

