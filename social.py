# coding=utf8
"""Reddit and Instagram module for Sopel"""
from sopel import module 
from sopel.modules import url

@module.rule('(?<!\w)r[/\s](\w+)')
def subreddit(bot, trigger): 
    bot.say(url.process_urls(bot, trigger, 'http://www.reddit.com/r/' + trigger.group(1)))


@module.rule('(?<!\w)u[/\s](\w+)')
def subreddit(bot, trigger): 
    bot.say(url.process_urls(bot, trigger, 'http://www.reddit.com/u/' + trigger.group(1)))

@module.rule('(?<!\w)W@(\w+)')
def subreddit(bot, trigger): 
    bot.say(url.process_urls(bot, trigger, 'http://www.instagram.com/' + trigger.group(1)))