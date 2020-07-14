#!/usr/bin/env python
# bhq_query.py - module for sopel to query blade head quarters site for knife data
# 
# Copyright (c) 2017 Casey Bartlett <caseytb@bu.edu>
# 
# See LICENSE for terms of usage, modification and redistribution.
#
from sopel import  *
import random
from itertools import repeat
@module.rule('.*carol baskin.*')
def baskin(bot, trigger):
    bot.say('THAT BITCH.')
