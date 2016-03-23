#!/usr/bin/env python
# blade_inventory - provides quick lookup for users
# 
# Copyright (c) 2016 Casey Bartlett <caseytb@bu.edu>
# 
# See LICENSE for terms of usage, modification and redistribution.
from sopel import web
from sopel.module import commands, example, NOLIMIT


def format_links(inventory_items):
    links = ""
    for i,l in enumerate(inventory_items):
        links += "{inventory_item}: {link} ".format(inventory_item=i,link=l)
    return links

@commands('inventory')
@example('.inventory fooobarrr')
def inventory(bot, trigger):
    """.inventory - Show the uses inventory list."""
    qnick = trigger.group(2)
    target_nick = ""
    if not qnick:
        carry_url = bot.db.get_nick_value(trigger.nick, 'blade_inventory')
        if not carry_url:
            return bot.msg(trigger.sender, "I don't have an inventory for you. " +
                    "Tell my what you're carrying like, .setinventory imgur.com/link1 imgur.com/link2")
        target_nick = trigger.nick
    else:
        target_nick = qnick.strip()
        inventory = bot.db.get_nick_value(target_nick, 'blade_inventory')
        if not carry_url:
            return bot.msg(trigger.sender, "{nickname} hasn't set an inventory. ".format(nickname=target_nick) +
                    "{nickname}: you can provide an inventory of your knives like, \".inventory imgur.com/link1 imgur.com/link2\"".format(nickname=target_nick))

    links = format_links(inventory)
    bot.say("{nick}'s inventory is: {urls}".format(nick=target_nick, urls=links))

@commands('setinventory', 'sinv', 'isc')
@example('.isc http://imgur.com/link_1 .. http://imgur.com/link_n')
def update_inventory(bot, trigger):
    """Set an inventory of your knives."""
    stripped_inventory = []
    if trigger.group(2):
        stripped_inventory = trigger.group(2).strip()
    else: 
        bot.reply('Give me a space delimited list of imgur url')
        return NOLIMIT
    inventory_links = stripped_inventory
    response = ""
    for link in inventory_links:
        body = web.get(link)
        if not body:
            response +="Invalid url \"{}\". ".format(link)
    if response:
        bot.reply(response)
        return NOLIMIT
    bot.db.set_nick_value(trigger.nick, 'blade_inventory', inventory_links)
    links = format_links(inventory_links)
    bot.reply("your inventory has been set to {urls}".format(urls=links))

@commands('carryfrominv', 'cfi')
@example('.cfi 1')
def update_carry(bot, trigger):
    index = trigger.group(2)
    if not index:
        return bot.reply('pleased provide the index of the link you want to set as your current carry')
    inventory = bot.db.get_nick_value(trigger.nick, 'blade_inventory')
    if not inventory:
        return bot.msg(trigger.sender, "I don't have an inventory for you. " +
                "Tell my what you're carrying like, .setinventory imgur.com/link1 imgur.com/link2")
    selected_carry = inventory[int(index)]
    bot.db.set_nick_value(trigger.nick, 'todayscarry', selected_carry)
    bot.reply("I have your carry set as {url} from index {idx}".format(url=trigger.group(2), idx=index))

@commands('append_blade', 'apb')
@example('.append_blade')
def add_item(bot, trigger):
    index = trigger.group(2)
    if not index:
        return bot.reply('pleased provide the index of the link you want to set as your current carry')
    inventory = bot.db.get_nick_value(trigger.nick, 'blade_inventory')
    if not inventory:
        return bot.msg(trigger.sender, "I don't have an inventory for you. " +
                "Tell my what you're carrying like, .setinventory imgur.com/link1 imgur.com/link2")
    selected_carry = inventory[int(index)]
    bot.db.set_nick_value(trigger.nick, 'todayscarry', selected_carry)
    bot.reply("I have your carry set as {url} from index {idx}".format(url=trigger.group(2), idx=index))


@commands('remove_blade', 'rmb')
@example('.remove_blade 2','.remove_blade imgur.com')
def del_item(bot, trigger):
    index_or_html = trigger.group(2)
    inventory = bot.db.get_nick_value(trigger.nick, 'blade_inventory')
    if not inventory:
        return bot.msg(trigger.sender, "I don't have an inventory for you. " +
                "Tell my what you're carrying like, .setinventory imgur.com/link1 imgur.com/link2")
    if not index_or_html:
        return bot.reply('Tell me which blade to remove by index, \".remove_blade 2\",' +
                'or by the url \".remove_blade imgur.com/link\"')
    if index_or_html.isdigit():
        index = int(index_or_html)

    selected_carry = inventory[int(index)]
    bot.db.set_nick_value(trigger.nick, 'todayscarry', selected_carry)
    bot.reply("I have your carry set as {url} from index {idx}".format(url=trigger.group(2), idx=index))

