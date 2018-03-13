# coding=utf-8
"""
mock.py - Sopel Mock Module
Copyright 2017, Casey T Bartlett
Licensed under the Eiffel Forum License 2.

http://sopel.chat
"""
from __future__ import unicode_literals, absolute_import, print_function, division

import time
import datetime
import random
from sopel.tools import Identifier
from sopel.tools.time import get_timezone, format_time
from sopel.module import commands, rule, priority, thread


@commands('mock')
def seen(bot, trigger):
    """Reports when and where the user was last seen."""
    if not trigger.group(2):
        bot.say(".mock <nick> - Mocks the user with their last comment repeated with random capitalization.")
        return
    nick = trigger.group(2).strip()
    if nick == bot.nick:
        bot.reply("You can't mock me!")
        return
    timestamp = bot.db.get_nick_value(nick, 'seen_timestamp')
    if timestamp:
        channel = bot.db.get_nick_value(nick, 'seen_channel')
        message = bot.db.get_nick_value(nick, 'seen_message')
        action = bot.db.get_nick_value(nick, 'seen_action')
        msg = ''.join(random.choice((str.upper,str.lower))(x) for x in message)
        #if Identifier(channel) == trigger.sender:
        #    if action:
        #        msg = msg + " in here, doing " + nick + " " + message
        #    else:
        #        msg = msg + " in here, saying " + message
        #else:
        #    msg += " in another channel."
        bot.say(msg)
    else:
        bot.say("SoRrY, i hAvEN'T sEen {} aRouND.".format(nick))

