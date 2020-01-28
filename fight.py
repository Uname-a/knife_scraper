#!/usr/bin/env python
# fight.py - fight another user, if they're available
# 
# Copyright (c) 2020 Casey Bartlett <caseytb@bu.edu>
# 
# See LICENSE for terms of usage, modification and redistribution.

from sopel.module import commands, example, NOLIMIT
from sopel.tools import Identifier
import datetime
import random

# Each user has the following associated state information (<<key: default>>)
# | <<player: nic>> 
#	+ <<hitPoints: 100>> 
#	+ <<xp: 0>> 
#	+ <<xl: 0>> 

# Xp levels
# start = 1
# stop  = log10(10000)
# nsteps = 5
# spacing = floor(logspace(start,stop,nsteps))
xlStop = 10000
xlScaling = 2
xlMinScaling = 3
xlMap = {0:10,
	1:31,
	2:100,
	3:316,
	4:1000,
	5:1778,
	6:3162,
	7:5623,
	8:xlStop}

# This is the format string used by __str__ of datetime.datetime
TimeFormat = "%Y-%m-%d %H:%M:%S.%f"

#fightStrings = [ "Bam boom pow! {source} stabs {target} for {damage} damage!",
# "Krakow! {source} filets {target} for {damage} damage!",
# "Reeee {source} uses loud screech on {target} dealing {damage} damage!",
# "Kaboom! {source} uses their dlc for SD to stab {target} for {damage} damage!"]

MissStrings = [ "Oh no {source} misses {target} and deals no damage and cannot attack for {delay} seconds"]

CritMissStrings = [ "Oh no {source} is confused and attacked themself for {damage} damage! and cannot attack for {delay} seconds"]

class nickDBAssocation:
	def __init__(self, db, UUID):
		self._db = db
		self._UUID = UUID
	@property
	def db(self):
		return self._db
	@property
	def UUID(self):
		return self._UUID

"""
DatabaseProperty is a convenience method for getting/setting values in a database
"""
class DatabaseProperty:
	def __init__(self, nickDB, propertyKey, propDefaultValue=0):
		self._nickStore = nickDB
		self._key  = propertyKey
		# validate that the property exists - if not create it (by setting the value in the DB)
		prop = self.value
		if not prop:
			self.value = propDefaultValue
	@property
	def key(self):
		return self._key
	@property
	def store(self):
		return self._nickStore
	@property
	def value(self):
		return self.store.db.get_nick_value(self.store.UUID, self.key)
	@value.setter
	def value(self, value):
		self.store.db.set_nick_value(self.store.UUID, self.key, value)

# convenience method to generate properties 
class DatabasePropertyFactory:
	def __init__(self, nickStore):
		self._nickStore = nickStore
	@property
	def nickStore(self):
		return self._nickStore
	def generate(self, propName, *kwargs):
		if "default" in kwargs:
			return DatabaseProperty(self.nickStore, propName, propDefaultValue=kwargs["default"])
		else:
			return DatabaseProperty(self.nickStore, propName)


class fighter:
	def __init__(self, db, nick):
		self._store = nickDBAssocation(db, nick)
		propFactory = DatabasePropertyFactory(self.store)
		#self.xl = propFactory("xl", default=1)
		self.xl = db.get_nick_value(nick, "xl")
		self.db = db
		self.nick = nick
		self.xl = db.get_nick_value(nick, "xl")
		self.delay = db.get_nick_value(nick, "delay")
		self.la = db.get_nick_value(nick, "la")
		self.speed = db.get_nick_value(nick, "speed")
		self.power = db.get_nick_value(nick, "power")
		self.defense = db.get_nick_value(nick, "defense")
		self.holy = db.get_nick_value(nick, "holy")

		if not self.la:
			self.la = 0
			db.set_nick_value(nick, "la", self.la)
		if not self.speed:
			self.speed = 0
			db.set_nick_value(nick, "speed", self.speed)
		if not self.power:
			self.power = 0
			db.set_nick_value(nick, "power", self.power)
		if not self.defense:
			self.defense = 0
			db.set_nick_value(nick, "defense", self.defense)
		if not self.holy:
			self.holy = 0
			db.set_nick_value(nick, "holy", self.holy)
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
		if not self.delay:
			self.delay = 0
			db.set_nick_value(nick, "delay", self.delay)
	@property
	def store(self):
		return self._store
	def receiveDamage(self, damage):
		msg = ""
		if self.hitPoints < damage:
			msg = " {nick} has died !".format(nick=self.nick)
			self.db.set_nick_value(self.nick, "hitPoints", 100 + (self.xl * 10))
		else:
			newhp = self.hitPoints - damage
			self.db.set_nick_value(self.nick, "hitPoints", newhp)
		return msg
	def receiveExperience(self, xp):
		self.db.set_nick_value(self.nick, "xp", self.xp + xp)
		return fightEvents.onXpChange(self, xp)
	def setXl(self, newXl):
		self.db.set_nick_value(self.nick, "xl", newXl)
	def setLA(self, newLA):
		self.db.set_nick_value(self.nick, "la", newLA)
	def adjustLA(self, adjust):
		self.db.set_nick_value(self.nick, "la", self.la + adjust)
	def setHealth(self, newHealth):
		self.db.set_nick_value(self.nick, "hitPoints", newHealth) 
	def setTime(self,delay):
		self.db.set_nick_value(self.nick, "delay", (datetime.datetime.now() + datetime.timedelta(seconds=delay)).strftime(TimeFormat))
	def setPower(self, newXl):
		self.db.set_nick_value(self.nick, "power", newXl)
	def setSpeed(self, newXl):
		self.db.set_nick_value(self.nick, "speed", newXl)
	def setDef(self, newXl):
		self.db.set_nick_value(self.nick, "defense", newXl)
	def setHoly(self, newXl):
		self.db.set_nick_value(self.nick, "holy", newXl)


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
		temp = 0
		while xlMap[newXl] < newXp:
			newXl += 1
			temp +=1
		xlDiff = newXl - aFighter.xl
		
		if xlDiff > 0:
			aFighter.setXl(newXl)
			aFighter.adjustLA(temp)
		else:
			return "You gained {totalLevels} XP".format(totalLevels=gainedXp)
		msg = "You gained {totalLevels} experience level".format(totalLevels=xlDiff)
		if xlDiff  > 1:
			msg += "s"
		return msg;
#todo add benifits to levels aka attack chance and armor?
def fightImpl(source, target):
	
	minDamage = 1
	maxDamage = 25
	minAttack = 1
	maxAttack = 100
	attack = random.randint(minAttack, maxAttack)
	if attack < 95 and attack > 5:
		attack += source.xl * 5
	index = 0 #to be removed with miss and crit changes
	damage = random.randint(minDamage, maxDamage) + source.xl 
	# add modifiers 
	attack -= target.defense * 3
	damage += source.power * 3

	targetDied = False
	sourceDied = False

	attackMissTransition=40
	damageMsg =""
	#attack hits
	if attack >= attackMissTransition:
		f = open("/home/botuser/.sopel/attack.txt")
		attack_list = f.readlines()
		max_attack_list = len(attack_list)
		attack_num = random.randint(0,max_attack_list-1)
		#crit hit double damage
		if attack >= 95:
			damage = damage * 2 
		baseMsg = attack_list[attack_num].format(source=source.nick, target=target.nick, damage=damage)
		damageMsg = target.receiveDamage(damage)
		if damageMsg:
			targetDied = True
	#attack misses
	elif attack < attackMissTransition:
		minDelay = 10
		maxDelay = 60
		delay = random.randint(minDelay, maxDelay)
		delay -= source.speed * 5
		# clamp delay to be 0
		delay = max(delay, 0)
		#crit misses attack self
		if attack <= 5:
			damage = damage * 2 
			baseMsg = CritMissStrings[index].format(source=source.nick, damage=damage, delay=delay)
		else:
			baseMsg = MissStrings[index].format(source=source.nick, target=target.nick, delay=delay)
		damageMsg = source.receiveDamage(damage)
		# source managed to kill themselves
		if damageMsg:
			sourceDied = True
			damageMsg  = "I can't believe you've done this. " + damageMsg
		source.setTime(delay)
	else:
		baseMsg = "uname fucked up somehow"

	xlChangedMessage = ""
	if targetDied:
		# A better method needs to be implemented, but basically the minimum fights would be 10
		# to level up
		minXpGain = int(xlMap[target.xl] / xlMinScaling if target.xl in xlMap else  xlStop / xlMinScaling)
		maxXpGain = int(xlMap[target.xl] / xlScaling if target.xl in xlMap else  xlStop / xlScaling)
		xpGained = random.randint(minXpGain, maxXpGain)
		xlChangedMessage = source.receiveExperience(xpGained)
	return "{base} {damage} {xl}".format(base=baseMsg, damage=damageMsg, xl=xlChangedMessage)

@commands('fight')
@example('.fight pf')
def fight(bot, trigger):
	# get this right away
	currentTime = datetime.datetime.now()
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
	nextTimeSourceAvailable  = currentTime
	try:
		nextTimeSourceAvailable = datetime.datetime.strptime(sourceFighter.delay, TimeFormat)
	except (ValueError, TypeError) as err:
		# just reset the delay so that next time this will work
		sourceFighter.setTime(0)
		pass
	if nextTimeSourceAvailable >= currentTime:
		duration = nextTimeSourceAvailable - currentTime
		# we lie here a little 
		durationInSeconds = int(duration.total_seconds()) if duration.total_seconds() > 0 else 1
		bot.reply('{target} cannot attack for {time} more seconds'.format(target=sourceNick, time=durationInSeconds))
		return
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
		currentXp = bot.db.get_nick_value(targetNick,'xp')
		remainingXp = xlMap[xl+1] - currentXp
		
		nextXl = xl+1
		if nextXl in xlMap:
			remainingXp = xlMap[nextXl] - currentXp
		else:
			remainingXp = "NO_NEXT_LEVEL"
		bot.say('{nick} has {hp} / {max} hp @ Level {xl} with {remainingXp} xp until the next level'.format(nick=targetNick, hp=hitpoints,max=100 + (xl*10), xl=xl, remainingXp=remainingXp))

@commands('level')
@example('.level power')
def Leveling(bot, trigger):
	sourceNick = trigger.nick
	trigger.group(2)
	if not trigger.group(2):
		bot.say('pick power, speed, or defense aka .level power')
		return
	power = Identifier(trigger.group(2).strip())
	
	target = fighter(bot.db, sourceNick)
	
	if target.la < 1:
		bot.say('you have no levels available to spend')
		target.setLA(0)
		return
	if power == "power" :
		target.setPower(target.power + 1)
		target.adjustLA(-1)
		bot.say('power is now {power} and you have {level}s left'.format(power=target.power,level=target.la))
	elif power == "speed":
		target.setSpeed(target.speed + 1)
		target.adjustLA(-1)
		bot.say('speed is now {power} and you have {level}s left'.format(power=target.speed,level=target.la))
	elif power == "defense":
		target.setDef(target.defense + 1)
		target.adjustLA(-1)
		bot.say('defense is now {power} and you have {level}s left'.format(power=target.defense,level=target.la))
	else:
		bot.say('pick power, speed, or defense aka .level power')
		return

@commands('heal')
@example('.heal fooobarrr')
def Healing(bot, trigger):
	if not trigger.group(2):
		bot.say('Heal who?')
		return
	targetNick = Identifier(trigger.group(2).strip())
	sourceNick = trigger.nick
	hitpoints = bot.db.get_nick_value(targetNick,'hitPoints')
	if not hitpoints:
		bot.say('I can''t find stats for {nick}'.format(nick=targetNick))
		return

	
	xl = bot.db.get_nick_value(targetNick,'xl')
	max = 100 + (xl*3)
	if hitpoints >= max:
		bot.say('{nick} is already at full health'.format(nick=targetNick))
		return
	else:
		targetFighter = fighter(bot.db, targetNick)
		SourceFighter = fighter(bot.db, sourceNick)
		minHeal = 5
		maxHeal = 25
		Heal = random.randint(minHeal, maxHeal)
		if (Heal + hitpoints) > max:
			Heal -= (Heal + hitpoints) - 100 + (xl*3)
		newHealth = hitpoints + Heal
		targetFighter.setHealth(newHealth)
		bot.say('{nick} has healed {target} for {heal} hit points and now has {hp} / {maxH} hitpoints'.format(nick=sourceNick,target=targetNick,heal=Heal,hp=hitpoints,maxH=max, xl=xl))
		sourceFighter.setHoly(SourceFighter.holy + 1)


@commands('smite')
@example('.smite pf')
def smite(bot, trigger):
	sourceNick = trigger.nick
	channel = trigger.sender
	
	if not trigger.group(2):
		bot.say('smite whosits?')
		return
	targetNick = Identifier(trigger.group(2).strip())
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
	if sourceFighter.holy > 0 :
		minHoly = 1
		maxHoly = 100
		Holy = random.randint(minHoly, maxHoly)
		if sourceFighter.holy >= 100:
			Holy = 80
			sourceFighter.setHoly(sourceFighter.holy - 100)
		else:
			if (sourceFighter.holy + Holy) > 80:
				Holy = 80
			else:
				Holy += sourceFighter.holy 
			sourceFighter.setHoly(0)
		if Holy >= 90:
			msg = '{nick} has called upon the gods to smite {target} and has been answered'.format(nick=sourceNick,target=targetNick)
			bot.say(msg)
			bot.say(mstargetFighter.receiveDamage(75))
		else:
			msg = '{nick} has called upon the gods to smite {target} and has been ignored'.format(nick=sourceNick,target=targetNick)
			bot.say(msg)
	else:
		bot.say('You have no holy points')
		return
	
