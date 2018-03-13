# bingo module

from sopel import  *
import random
from itertools import repeat

@module.rule('.bingo.*')
@module.rule('.Bingo.*')
@module.rule('.BINGO.*')
def bingo(bot, trigger):
    bot.say('BINGO Time! https://i.imgur.com/fbWAzDh.png')

