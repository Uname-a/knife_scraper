# bingo module

from sopel import  *
import random
from itertools import repeat

@module.rule('.[Pp][Oo][Tt][Aa][Tt][Oo].*')
def bingo(bot, trigger):
    bot.say('POTATO  https://usercontent.irccloud-cdn.com/file/qJgOPIi3/potato.jpg')

