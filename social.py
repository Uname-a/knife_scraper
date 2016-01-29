# coding=utf8
"""Reddit and Instagram module for Sopel"""
from sopel import module 
from sopel.modules import url

@module.rule('.*\Wr[/\s](\w+)')
@module.rule('^r[/\s](\w+)')
def subreddit(bot, trigger): 
    _url = 'http://www.reddit.com/r/' + trigger.group(1)
#    message = urlmessage(bot, trigger, url)
    bot.say(_url)


@module.rule('.*\Wu[/\s](\w+)')
@module.rule('^u[/\s](\w+)')
def reddituser(bot, trigger): 
    _url = 'http://www.reddit.com/u/' + trigger.group(1)
#    message = urlmessage(bot, trigger, url)
    bot.say(_url)

@module.rule('.*\W@(\w+)')
@module.rule('^@(\w+)')
def instagram(bot, trigger): 
    _url = 'http://www.instagram.com' + trigger.group(1)
#    message = urlmessage(bot, trigger, url)
    bot.say(_url)

def urlmessage(bot, trigger, url):
    results = url.process_urls(bot, trigger, url)
    for title in results[:4]:
        message = url + '[ %s ]' % (title)
    return message
