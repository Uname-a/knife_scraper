#!/bin/bash
# uninstall.sh - shell script to deleted files to sopel runtime directory
# 
# Copyright (c) 2015 Casey Bartlett <caseytb@bu.edu>
# 
# See LICENSE for terms of usage, modification and redistribution.

# deletes python files in sopel modules directory
# should use pip or setup.py

sopel_dir = ~/.sopel/knifeclub_modules

if [ -d $sopel_dir ]
then
	rm $sopel_dir/extract_blade_info.py
	rm $sopel_dir/ddg.py
	rm $sopel_dir/bhq_query.py
fi

