#!/usr/bin/env python
# extract_blade_info.py - collections of classes and functions for parsing blade_head_quarter's data into an IRC compatible format
# 
# Copyright (c) 2015,2016 Casey Bartlett <caseytb@bu.edu>
# 
# See LICENSE for terms of usage, modification and redistribution.

from bs4 import BeautifulSoup as bs
from urllib.request import urlopen, URLError
from collections import OrderedDict
from sopel import formatting
from string import Template
from bhq_inventory_items import INVENTORY_ITEMS, BHQNAME_TO_DBNAME 
import datetime

def replaceDictKeys(key_map, dict_to_change):
    d = dict()
    for k,v in key_map.items():
        if k in dict_to_change:
            d[v] = dict_to_change[k]
    return d

def getSubDict(keys, theDict):
    d = dict()
    for k in keys:
        d[k] = theDict[k]

def strip_units(value):
    """
    Lazy way to strip units - need much better parsing here to detect units
    There must be a library somewhere to do this
    """
    # inches to cm
    if value.endswith("\""):
        v = value.replace("\"","")
        return float(v)*0.0254
    # ounces to grams
    elif value.endswith(" oz."):
        v = value.replace(" oz.","")
        return float(v)*28.35
    # no translation needed
    else:
        return value

# for future statistics - also should get the price in db as text and instances of price should be PriceQuantity
class PriceQuantity:
    def __init__(self, dollars, cents):
        self.dollars = int(dollars)
        self.cents = int(cents)
    def __add__(self, other):
        total_cents = self.cents + other.cents
        remaining_cents = total_cents % 100
        dollars_from_cents = total_cents / 100
        return PriceQuantity(dollars_from_cents, remaining_cents)
    def __repr__(self):
        return "{dollars}.{cents:02d}".format(dollars=self.dollars,cents=self.cents)
    def __lt__(self, other):
        return 100*self.dollars + self.cents < 100*other.dollars + other.cents 
    def __gt__(self,other):
        return 100*self.dollars + self.cents > 100*other.dollars + other.cents 
    def __eq__(self,other):
        return 100*self.dollars + self.cents == 100*other.dollars + other.cents 

def parse_price_element(price_element):
    """
    @price_element a text string like u'Our Price: 134.23'
    """ 
    items = price_element.split(":")
    price = items[1].strip()
    price_no_symbol = price.strip("$")
    price_no_symbol = price_no_symbol.replace(",","")
    dollars, cents =price_no_symbol.split(".")
    return PriceQuantity(dollars,cents)

def parse_unit(the_text):
    return the_text
def parse_text(the_text):
    return the_text
def spec_parse_rules( key ):
    parse_rules =  {
        "Overall Length" : parse_unit,
        "Blade Length" : parse_unit,
        "Closed Length" : parse_unit,
        "Cutting Edge Length" : parse_unit,
        "Steel" : parse_text,
        "Handle Material" : parse_text,
        "Weight" : parse_unit,
        "Clip" : parse_text,
        "Tip Carry" : parse_text
    }
    # assume parse_text otherwise
    return parse_rules.get(key,parse_text)

def spec_items_to_dict(spec_items):
    spec_dict= dict()
    for s in spec_items:
        ss = s.text.split(":")
        # means we have two items
        if len(ss) == 2:
            key = ss[0].strip()
            value = ss[1].strip()
            parser = spec_parse_rules(key)
            spec_dict[key] = parser(value)
        elif s.text == "Made in USA":
            spec_dict["Country of Origin"] = "USA"
        else:
            print("Not sure what to do here")
    return spec_dict

def query_kc_knife(endpoint):
    try:
        page = urlopen("{url}".format(url=endpoint))
    except URLError as e:
        print(e.reason)
    soup = bs(page)
    price = soup.find("span",{"itemprop":"price"}).text
    description = soup.find("div", {"class":"description"})
    major_item_details = description.findAll("b")
    model = major_item_details[1].text
    brand = description.find("i").text

    all_specs = soup.find("div",{"class":'specs'})
    spec_items = all_specs.findAll("li")
    spec_dict = spec_items_to_dict(spec_items)
    knife = OrderedDict()
    knife.update(spec_dict)

    today = datetime.date.today()
    knife["Link"] = endpoint
    knife["Brand"] = brand
    knife["Model"] = model
    knife["Date Added"] = today.strftime(u"%x")
    knife["Vendor Name"] = u"Knife Center"
    knife["Vendor ID"] = soup.find("td",{"class":'sku'}).text
    knife["Price"] = price
    return knife

def query_bhq_knife(endpoint):
    try:
        page = urlopen("{url}".format(url=endpoint))
    except URLError as e:
        print(e.reason)
    soup = bs(page)

    specs=soup.findAll('div', {'class':"prodSpecs tabContent show-this-tab"})
    # if we can't find the item # then this isn't the appropriate page to continue parsing
    if not specs:
        return []
    specKeys = specs[0].findAll('span', {"class":"attName"})
    specValues = specs[0].findAll('span', {"class":"attValue"})

    # BHQ item number
    item = soup.findAll("span", {"class":"itemNumber"})
    # couldn't find the item - just return empty
    if not item:
        return []
    bhq_item_string = item[0].text
    bhq_item_num  = bhq_item_string.split("-")[-1]

    knife = OrderedDict()
    for k,v in zip(specKeys,specValues):
        #vs = strip_units(v.text)
        key = k.text.strip(":")
        knife[key] = v.text

    # Price - probably need to use price repr
    item_selection= soup.findAll("span",{"class": "item-descr-price"})
    price_element = item_selection[0].find("div", {"class" : "price" }).text
    #price = parse_price_element(price_element)
    if price_element.strip() == "Sold":
        price = "Out of Stock"
    else:
        items = price_element.split(":")
        price = items[1].strip()
        price = price.strip("$")
    
    today = datetime.date.today()
    knife["Link"] = endpoint
    knife["Date Added"] = today.strftime(u"%x")
    knife["Vendor Name"] = u"BHQ"
    knife["Vendor ID"] = str(bhq_item_num)
    knife["Price"] = str(price) 
    return knife

def query_test_knife():
    try:
        page = urlopen("{file_full_path}{file_name}".format(file_full_path='file:///home/casey/src/knife_scraper/html/',file_name='spyderco.html'))
    except URLError as e:
        print(e.reason)
    soup = bs(page)
    specs=soup.findAll('div', {'class':"prodSpecs tabContent show-this-tab"})
    specKeys = specs[0].findAll('span', {"class":"attName"})
    specValues = specs[0].findAll('span', {"class":"attValue"})
    knife = OrderedDict()
    for k,v in zip(specKeys,specValues):
        vs = strip_units(v.text)
        key = k.text.strip(":")
        knife[key] = vs

    item_selection= soup.findAll("span",{"class": "item-descr-price"})
    price_element = item_selection[0].find("div", {"class" : "price" }).text
    print(price_element)
    price = parse_price_element(price_element)
    
    # these attributes have to be pulled from somewhere else
    knife["Date Added"] = "11/18/2015"
    knife["Vendor Name"] = "BHQ"
    knife["Vendor ID"] = 10801
    knife["Price"] = price
    return knife

class KnifeFormatter():
    '''
    We are just going to take input from the user and accept only items in the dict
    We'll use the formatting module from sopel
    '''
    def __init__(self):
        self.format_string = self.setupDefault()
    # function due to the coloring
    def setupDefault(self):
        # to check the string construct 
        fmt = Template("The $brand $handle_material $model" +\
                " has a $blade_lengthMKS blade" +\
                " made of $blade_material steel" +\
                " (weight of $massMKS)" +\
                " priced at [ $$" +\
                formatting.color("$price",fg=formatting.colors.GREEN)+\
                " ] " +\
                " $url")
        try:
            fmt.safe_substitute(**INVENTORY_ITEMS)
            return fmt
        except exceptions.KeyError as e:
           print("Key {} not available in".format(e))
           return ""
    def setFormat(self,format_string):
        # if we're successful return empty
        try:
            tmp = Template(format_string)
            self.format_string = tmp.safe_substitute(**INVENTORY_ITEMS)
            return  []
        except exceptions.KeyError as e:
            return "Key {} not available in knife".format(e)
    # knife is expected to be a dict
    def formattedKnife(self,knife):
        return self.format_string.safe_substitute(**knife)

def run():
    knife = query_test_knife()
    print(knife)

# Test with fixed URL (avoid DDG here)
def test_run():
    # Get this url with ddg search api
    query_string = "paramilitary 2"
    url= "http://www.bladehq.com/item--Spyderco-Paramilitary-2--7920"
    knife = query_bhq_knife(url)
    print("This is the knife:")
    print(knife)
    d = replaceDictKeys(BHQNAME_TO_DBNAME,knife)
    if knife:
        #ib = inventoryDatabase()
        #ib.add_knife(knife)
        kf = KnifeFormatter()
        print(kf.formattedKnife(d))
    else:
        print("I couldn't find the information {knife} but here's the first url I could find: {url}".format(knife = query_string,url=url))

if __name__ == '__main__':
    run()

