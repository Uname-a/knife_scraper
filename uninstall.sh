#!/bin/bash
# Copies python files into sopel modules directory... pretty horrible actually
sopel_dir = ~/.sopel/knifeclub_modules

if [ -d $sopel_dir ]
then
	rm $sopel_dir/extract_blade_info.py
	cp $sopel_dir/ddg.py
	cp $sopel_dir/bhq_query.py
fi

