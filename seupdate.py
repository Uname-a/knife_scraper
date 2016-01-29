#!/usr/bin/env python
# extract_blade_info.py - collections of classes and functions for parsing blade_head_quarter's data into an IRC compatible format
#
# Copyright (c) 2016 Casey Bartlett <caseytb@bu.edu>
#
# See LICENSE for terms of usage, modification and redistribution.

from __future__ import unicode_literals, absolute_import, print_function, division

import sopel.loader
import sopel.module
import subprocess
from sopel.modules.reload import f_reload
from se_config import install_directory


@sopel.module.nickname_commands('seup')
def f_update(bot, trigger):
    if not trigger.admin:
        return
    """Pulls the latest versions of SharpExtension modules from Git"""

    proc = subprocess.Popen('/usr/bin/git pull',
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, shell=True,
                            cwd=install_directory)
    bot.reply(proc.communicate()[0])

    f_reload(bot, trigger)
