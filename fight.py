#!/usr/bin/env python
# fight.py - fight another user, if they're available
# 
# Copyright (c) 2020 Casey Bartlett <caseytb@bu.edu>
# 
# See LICENSE for terms of usage, modification and redistribution.

from sopel.module import commands, example, NOLIMIT
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
	1:31
	2:100
	3:316
	4:1000}

fightStrings = [ "Bam boom pow! {source} stabs {target} for {damage} damage!",
 "Krakow! {source} filets {target} for {damage} damage!",
 "Reeee {source} uses loud screech on {target} dealing {damage} damage!",
 "Kaboom! {source} uses their dlc for SD to stab {target} for {damage} damage!"]

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
	def onXpChange(fighter, gainedXp):
		newXl = fighter.xl
		newXp = gainedXp + fighter.xp
		while xlMap[newXl] < newXp:
			newXl += 1
		xlDiff = newXl - fighter.xl
		if xlDiff > 0
			fighter.setXl(newXl)
		else:
			return ""
		msg = "You gained {totalLevels} experience level".format(xlDiff)
		if xlDiff  > 1:
			msg += "s"
		return msg;

def fight(source, target):
	maxIndex = len(fightStrings) - 1
	minDamage = 1
	maxDamage = 10
	minXpGain = 2
	maxXpGain = 15
	index = random.randint(0, maxIndex)
	damage = random.randint(minDamage, maxDamage)
	baseMsg = fightStrings[index].format(source=source, target=target, damage=damage)
	damageMsg = target.receiveDamage(damage)
	xlChangedMessage = ""
	if damageMsg:
		# Generate some random xp:
		xpGained = random.randint(minXpGain, maxXpGain)
		xlChangedMessage = fighter.receiveExperience(xpGained)
	return "{base} {damage} {xl}".format(baseMsg, damageMsg, xlChangedMessage)

@commands('fight')
@commands('.fight pf')
def fight(bot, trigger):
	sourceNick = trigger.nick
	channel = trigger.channel
	targetNick = trigger.group(2)
	if targetNick not in bot.channels[channel].users:
		bot.reply('{target} is not in this channel [[{channel}]]'.format(target=targetNick, channel=channel))
	# load the fighters
	sourceFighter = fighter(bot.db, sourceNick)
	targetFighter = fighter(bot.db, targetNick)
	msg = fight(sourceFighter, targetFighter)
	sopel.say(msg)
