# bingo module

from sopel import  *
import random
from itertools import repeat

@module.rule('.[Kk][Ee][Tt][Oo].*')
def bingo(bot, trigger):
    bot.say('KETO POWER! https://i.imgur.com/AbNOPA9.png')

