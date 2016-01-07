#!/usr/bin/env python
# bhq_query.py - module for sopel to query blade head quarters site for knife data
# 
# Copyright (c) 2015 Casey Bartlett <caseytb@bu.edu>
# 
# See LICENSE for terms of usage, modification and redistribution.

from sopel import  *

@module.commands('wtc')
def knife(bot, trigger):
    bot.reply("Look I respond to the wtc command now!")
