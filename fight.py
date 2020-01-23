#!/usr/bin/env python
# fight.py - fight another user, if they're available
# 
# Copyright (c) 2020 Casey Bartlett <caseytb@bu.edu>
# 
# See LICENSE for terms of usage, modification and redistribution.

from sopel.module import commands, example, NOLIMIT
from sopel.tools import Identifier
import random

# Each user has the following associated state information (<<key: default>>)
# | <<player: nic>> 
#	+ <<hitPoints: 100>> 
#	+ <<xp: 0>> 
#	+ <<xl: 0>> 

# Xp levels
# start = 1
# stop  = log10(1000)
# nsteps = 5
# spacing = floor(logspace(start,stop,nsteps))
xlMap = {0:10,
	1:31,
	2:100,
	3:316,
	4:1000}

fightStrings = [ "Bam boom pow! {source} stabs {target} for {damage} damage!",
 "Krakow! {source} filets {target} for {damage} damage!",
 "Reeee {source} uses loud screech on {target} dealing {damage} damage!",
 "Kaboom! {source} uses their dlc for SD to stab {target} for {damage} damage!"]

MissStrings = [ "Oh no {source} misses {target} and deals no damage"]

CritMissStrings = [ "Oh no {source} is confused and attacked themself for {damage} damage!"]


class fighter:
	def __init__(self, db, nick):
		self.db = db
		self.nick = nick
		self.xl = db.get_nick_value(nick, "xl")
		if not self.xl:
			self.xl = 0
			db.set_nick_value(nick, "xl", self.xl)
		self.xp = db.get_nick_value(nick, "xp")
		if not self.xp:
			self.xp = 0
			db.set_nick_value(nick, "xp", self.xp)
		self.hitPoints = db.get_nick_value(nick, "hitPoints")
		if not self.hitPoints:
			self.hitPoints=100
			db.set_nick_value(nick, "hitPoints", self.hitPoints)
	def receiveDamage(self, damage):
		msg = ""
		if self.hitPoints < damage:
			msg = " {nick} has died !".format(nick=self.nick)
			self.db.set_nick_value(self.nick, "hitPoints", 100)
		else:
			newhp = self.hitPoints - damage
			self.db.set_nick_value(self.nick, "hitPoints", newhp)
		return msg
	def receiveExperience(self, xp):
		self.db.set_nick_value(self.nick, "xp", xp)
		return fightEvents.onXpChange(self, xp)
	def setXl(self, newXl):
		self.db.set_nick_value(self.nick, "xl", newXl)

			
		

class fightEvents:
	# Event for "on xp change" - Don't assume only one level can be increased at one
	# time
	# if no xl change:
	# - return
	# if xl changes:
	# - write xl to database
	# - generate message
	def onXpChange(aFighter, gainedXp):
		newXl = aFighter.xl
		newXp = gainedXp + aFighter.xp
		while xlMap[newXl] < newXp:
			newXl += 1
		xlDiff = newXl - aFighter.xl
		if xlDiff > 0:
			aFighter.setXl(newXl)
		else:
			return ""
		msg = "You gained {totalLevels} experience level".format(totalLevels=xlDiff)
		if xlDiff  > 1:
			msg += "s"
		return msg;
#todo add benifits to levels aka attack chance and armor?
def fightImpl(source, target):
	maxIndex = len(fightStrings) - 1
	minDamage = 1
	maxDamage = 25
	minXpGain = 2
	maxXpGain = 30
	minAttack = 1
	maxAttack = 100
	attack = random.randint(minAttack, maxAttack)
	if attack <=95 or attack >= 5:
		attack += source.xl
	index = random.randint(0, maxIndex)
	damage = random.randint(minDamage, maxDamage)
	damageMsg =""
	
	if attack >= 50 and attack < 95:
		baseMsg = fightStrings[index].format(source=source.nick, target=target.nick, damage=damage)
		damageMsg = target.receiveDamage(damage)
	elif attack >= 95:
		damage = damage * 2
		baseMsg = fightStrings[index].format(source=source.nick, target=target.nick, damage=damage)
		damageMsg = target.receiveDamage(damage)
	elif attack < 50 and attack > 5:
		baseMsg = fightStrings[index].format(source=source.nick, target=target.nick)
		damageMsg = target.receiveDamage(damage)
	elif attack <= 5:
		damage = damage / 2
		baseMsg = fightStrings[index].format(source=source.nick, damage=damage)
		damageMsg = source.receiveDamage(damage)
	else:
		baseMsg = fightStrings[index].format(source=source.nick, target=target.nick, damage=damage)
		damageMsg = target.receiveDamage(damage)
	xlChangedMessage = ""
	
	if damageMsg:
		# Generate some random xp:
		xpGained = random.randint(minXpGain, maxXpGain)
		xlChangedMessage = source.receiveExperience(xpGained)
	return "{base} {damage} {xl}".format(base=baseMsg, damage=damageMsg, xl=xlChangedMessage)

@commands('fight')
@example('.fight pf')
def fight(bot, trigger):
	sourceNick = trigger.nick
	channel = trigger.sender
	if not trigger.group(2):
		bot.say('fight whosits?')
		return
	targetNick = Identifier(trigger.group(2).strip())
	if targetNick == sourceNick:
		bot.say('Are u slow son?')
		return
	if targetNick == "knifebot":
		bot.say('knifebot dodges with robotic skill')
		return
	if channel not in bot.channels:
		bot.reply('You can''t fight here!')
		return
	if targetNick not in bot.channels[channel].users:
		bot.reply('{target} is not in this channel [[{channel}]]'.format(target=targetNick, channel=channel))
		return
	# load the fighters
	sourceFighter = fighter(bot.db, sourceNick)
	targetFighter = fighter(bot.db, targetNick)
	msg = fightImpl(sourceFighter, targetFighter)
	bot.say(msg)

@commands('fstat')
@example('.fstat fooobarrr')
def fighterStatus(bot, trigger):
	if not trigger.group(2):
		bot.say('fighter status for who?')
		return
	targetNick = Identifier(trigger.group(2).strip())
	hitpoints = bot.db.get_nick_value(targetNick,'hitPoints')
	xl = bot.db.get_nick_value(targetNick,'xl')
	if not hitpoints:
		bot.say('I can''t find stats for {nick}'.format(nick=targetNick))
		return
	else:
		bot.say('{nick} has {hp} hit points / 100 @ XL {xl}'.format(nick=targetNick, hp=hitpoints, xl=xl))

