# coding=utf8
"""Reddit and Instagram module for Sopel"""
from sopel import module 
from sopel.modules import url

@module.rule('.*\W[/\s]r/(\w+)')
@module.rule('^/?r/(\w+)')
def subreddit(bot, trigger): 
    _url = 'http://www.reddit.com/r/' + trigger.group(1)
    message = urlmessage(bot, trigger, _url)
    bot.say(message)


@module.rule('.*\W[/\s]u/(\w+)')
@module.rule('^/?u/(\w+)')
def reddituser(bot, trigger): 
    _url = 'http://www.reddit.com/u/' + trigger.group(1)
    message = urlmessage(bot, trigger, _url)
    bot.say(message)

@module.rule('.*\W@(\w+)')
@module.rule('^@(\w+)')
def instagram(bot, trigger): 
    _url = 'http://www.instagram.com/' + trigger.group(1)
    message = urlmessage(bot, trigger, _url)
    bot.say(message)

def urlmessage(bot, trigger, _url):
    results = url.process_urls(bot, trigger, [_url])
    message = _url
    for title, domain in results:
        message += ' [ ' + title + ' ]'
    return message
