# bingo module

from sopel import  *
import random
from itertools import repeat

@module.rule('.[Bb][Ii][Nn][Gg][Oo].*')
def bingo(bot, trigger):
    bot.say('BINGO Time! https://i.imgur.com/fbWAzDh.png')

