#!/bin/bash
# Copies python files into sopel modules directory... pretty horrible actually
sopel_dir=~/.sopel/knifeclub_modules
# install.sh - shell script to copy files to sopel runtime directory
# 
# Copyright (c) 2015 Casey Bartlett <caseytb@bu.edu>
# 
# See LICENSE for terms of usage, modification and redistribution.

# Copies python files into sopel modules directory
# should use pip or setup.py
sopel_dir=~/.sopel/knifeclub_modules

if [ -d $sopel_dir ]
then
	cp extract_blade_info.py $sopel_dir
	cp ddg.py $sopel_dir
	cp bhq_query.py $sopel_dir
fi
