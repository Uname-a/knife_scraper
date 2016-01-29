# coding=utf8
"""Reddit and Instagram module for Sopel"""
from sopel import module 
from sopel.modules import url

@module.rule('.*[/\s]r/(\w+)')
@module.rule('^/?r/(\w+)')
def subreddit(bot, trigger): 
    _url = 'http://www.reddit.com/r/' + trigger.group(1)
    message = urlmessage(bot, trigger, _url)
    bot.say(_url)


@module.rule('.*[/\s]u/(\w+)')
@module.rule('^/?u/(\w+)')
def reddituser(bot, trigger): 
    _url = 'http://www.reddit.com/u/' + trigger.group(1)
    message = urlmessage(bot, trigger, _url)
    bot.say(_url)

@module.rule('.*\W@(\w+)')
@module.rule('^@(\w+)')
def instagram(bot, trigger): 
    _url = 'http://www.instagram.com/' + trigger.group(1)
    message = urlmessage(bot, trigger, _url)
    bot.say(_url)

def urlmessage(bot, trigger, _url):
    results = url.process_urls(bot, trigger, [_url])
    message = _url
    for title in results[:4]:
        message = url + '[ %s ]' % (title)
    return message
