from sopel import  *
import random
from itertools import repeat

@module.rule('.[Vv][Ee][Rr][Oo].*')
def vero(bot, trigger):
    bot.say('check out veroengineering.com')

