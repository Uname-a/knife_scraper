from sopel import *
from sopel.tools import Identifier, iterkeys
import random

qdb = "/home/botuser/.sopel/quote.db"

@module.commands('addquote')
def addquote(bot, trigger):
    command = trigger.group(1)
    quote = trigger.group(2)
    f = open(qdb, 'a')
    f.write("\n%s" % quote)
    f.close()
    bot.reply('Added it...')


@module.commands('quote')
def quote(bot, trigger):
    with open(qdb, 'r') as f:
        if trigger.group(2):
            search_string = trigger.group(2).strip()
            lines = [ x for x in list(f) if search_string in x]
            if lines:
                line = random.choice(lines)
                bot.say(line)
            else:
                bot.say("no quote found with search term {}".format(search_string))
        else:
            line = random.choice(list(f))
            bot.say(line)

@module.commands('gquote')
def gquote(bot, trigger):
    if not trigger.group(2):
        return bot.reply(".gquote <nick> - Quotes the last thing <nick> said. Who is Nick?")
    nick = trigger.group(2).strip()
    timestamp = bot.db.get_nick_value(nick, 'seen_timestamp')
    if timestamp:
        if nick == bot.nick:
            return bot.reply("you can't quote me ya dingus!")
        quote = bot.db.get_nick_value(nick, 'seen_message')
        quote_string = "<{user_nick}> {user_quote}".format(user_nick = nick,  user_quote = quote)
        with open(qdb,'a') as f:
            f.write("\n" + quote_string)
        bot.reply('Added quote: \"{qs}\"'.format(qs=quote_string))
    else:
        return bot.reply("I've never seen {} before ya dingus!".format(nick))
