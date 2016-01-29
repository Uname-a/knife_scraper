# coding=utf8
"""Junglas module for Sopel"""
from sopel import module
import random
from itertools import repeat, imap

def random_cap(c):
   if random.randint(0, 1):
       return c.upper()
   return c.lower()


def random_chars(s):
   new_s = []
   for c in s:
       new_s.extend(imap(random_cap, repeat(c, random.randint(1, 10))))
   return ''.join(new_s)

#print random_chars('hoonglass')


@module.rule('.*\W((j+u+)|(h+oo+))n+g+l+a+s+')
@module.rule('^((j+u+)|(h+oo+))n+g+l+a+s+')
def junglas(bot, trigger): 
    bot.say(random_chars('hoonglass!'))
