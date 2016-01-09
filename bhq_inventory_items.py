#!/usr/bin/env python
# extract_blade_info.py - collections of classes and functions for parsing blade_head_quarter's data into an IRC/sqlite3 compatible format
# 
# Copyright (c) 2016 Casey Bartlett <caseytb@bu.edu>
# 
# See LICENSE for terms of usage, modification and redistribution.

from collections import OrderedDict

INVENTORY_ITEMS =  OrderedDict([("date_added","text"),
    ("overall_lengthMKS","real"),
    ("blade_lengthMKS","real"),
    ("cutting_edgeMKS","real"),
    ("blade_thicknessMKS","real"),
    ("blade_material","text"),
    ("blade_style","text"),
    ("blade_grind","text"),
    ("blade_finish","text"),
    ("handle_lengthMKS","real"),
    ("handle_thicknessMKS","real"),
    ("handle_material","text"),
    ("color","text"),
    ("frame_liner","text"),
    ("massMKS","real"),
    ("configuration","text"),
    ("clip_configurations","text"),
    ("knife_type","text"),
    ("open_type","text"),
    ("lock_type","text"),
    ("brand","text"),
    ("url","text"),
    ("model","text"),
    ("model_number","text"),
    ("country_of_origin","text"),
    ("usage","text"),
    ("price","real"),
    ("vendor_id","text"),
    ("vendor","text")])

BHQNAME_TO_DBNAME= dict({
    "Overall Length":"overall_lengthMKS",
    "Blade Length":"blade_lengthMKS",
    "Cutting Edge":"cutting_edgeMKS",
    "Blade Thickness":"blade_thicknessMKS",
    "Blade Material":"blade_material",
    "Blade Style":"blade_style",
    "Blade Grind":"blade_grind",
    "Finish":"blade_finish",
    "Edge Type":"edge_type",
    "Handle Length":"handle_lengthMKS",
    "Handle Thickness":"handle_thicknessMKS",
    "Handle Material":"handle_material",
    "Color":"color",
    "Frame/Liner":"frame_liner",
    "Weight":"massMKS",
    "User":"configuration",
    "Pocket Clip":"clip_configurations",
    "Knife Type":"knife_type",
    "Opener":"open_type",
    "Lock Type":"lock_type",
    "Brand":"brand",
    "Link":"url",
    "Model":"model",
    "Model Number":"model_number",
    "Country of Origin":"country_of_origin",
    "Best Use":"usage",
    "Price":"price",
    "Vendor ID":"vendor_id",
    "Vendor Name":"vendor",
    "Date Added":"date_added"})

