from sopel import web
from sopel.module import commands, example, NOLIMIT

@commands('carry')
@example('.carry fooobarrr')
def carry(bot, trigger):
    """.carry show what nickname is carrying today."""

    qnick = trigger.group(2)
    target_nick = ""
    if not qnick:
        carry_url = bot.db.get_nick_value(trigger.nick, 'todayscarry')
        if not carry_url:
            return bot.msg(trigger.sender, "I don't know what you're carrying. " +
                    "Tell my what you're carrying like, .setcarry imgur.com")
        target_nick = trigger.nick
    else:
        target_nick = qnick.strip()
        carry_url = bot.db.get_nick_value(target_nick, 'todayscarry')
        if not carry_url:
            return bot.msg(trigger.sender, "I don't know what {nickname} is carrying. ".format(nickname=target_nick) +
                    "{nickname}: tell my what you're carrying like, .setcarry imgur.com".format(nickname=target_nick))

    bot.say("{nick} is currently carrying {url}".format(nick=target_nick, url=carry_url))

@commands('setcarry', 'sc')
@example('.sc http://imgur.com')
def update_carry(bot, trigger):
    """Set the knife you're carrying today."""
    selection = trigger.group(2)
    if not selection:
        bot.reply('Give me a list of imgur urls')
        return NOLIMIT
    body = web.get(selection)
    if not body:
        return bot.reply("Invalid url {}".format(selection))
    bot.db.set_nick_value(trigger.nick, 'todayscarry', trigger.group(2))
    bot.reply("I have your carry set as {url}".format(url=trigger.group(2)))

