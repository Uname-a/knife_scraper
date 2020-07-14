from sopel.module import commands, example, NOLIMIT
from requests import get

@commands('gc', 'guncarry', 'gatcarry')
@example('.gc Sanity')
def carry(bot, trigger):
    """.carry show what gat nickname is carrying today."""

    qnick = trigger.group(2)
    target_nick = ""
    if not qnick:
        carry_url = bot.db.get_nick_value(trigger.nick, 'todaysguncarry')
        if not carry_url:
            return bot.msg(trigger.sender, "I don't know what you're carrying. " +
                    "Tell my what you're carrying like, .sgc imgur.com")
        target_nick = trigger.nick
    else:
        target_nick = qnick.strip()
        carry_url = bot.db.get_nick_value(target_nick, 'todaysguncarry')
        if not carry_url:
            return bot.msg(trigger.sender, "I don't know what {nickname} is carrying. ".format(nickname=target_nick) +
                    "{nickname}: tell me what gun you're carrying like, .sgc imgur.com".format(nickname=target_nick))

    bot.say("{nick} is currently zap carrying {url}".format(nick=target_nick, url=carry_url))

@commands('setguncarry', 'sgc', 'setgatcarry')
@example('.sgc http://imgur.com')
def update_carry(bot, trigger):
    """Set the gun you're carrying today."""
    selection = trigger.group(2)
    if not selection:
        bot.reply('Give me a list of imgur urls')
        return NOLIMIT
    body = get(selection)
    if not body:
        return bot.reply("Invalid url {}".format(selection))
    bot.db.set_nick_value(trigger.nick, 'todaysguncarry', trigger.group(2))
    bot.reply("I have your gat carry set as {url}".format(url=trigger.group(2)))
