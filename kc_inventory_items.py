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
    ("closed_lengthMKS","real"),
    ("blade_thicknessMKS","real"),
    ("blade_material","text"),
    ("handle_lengthMKS","real"),
    ("handle_weightMKS","real"),
    ("handle_material","text"),
    ("massMKS","real"),
    ("clip_configurations","text"),
    ("brand","text"),
    ("url","text"),
    ("model","text"),
    ("country_of_origin","text"),
    ("price","real"),
    ("vendor_id","text"),
    ("vendor","text")])

KCNAME_TO_DBNAME= dict({
    "Overall Length":"overall_lengthMKS",
    "Blade Length":"blade_lengthMKS",
    "Cutting Edge Length":"cutting_edgeMKS",
    "Steel":"blade_material",
    "Closed Length":"handle_lengthMKS",
    "Handle Material":"handle_material",
    "Weight":"massMKS",
    "Clip":"clip_configurations",
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

