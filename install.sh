#!/bin/bash
# Copies python files into sopel modules directory... pretty horrible actually
sopel_dir = ~/.sopel/knifeclub_modules

if [ -d $sopel_dir ]
then
	cp extract_blade_info.py $sopel_dir
	cp ddg.py $sopel_dir
	cp bhq_query.py $sopel_dir
fi
