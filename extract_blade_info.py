#!/usr/bin/env python
# extract_blade_info.py - collections of classes and functions for parsing blade_head_quarter's data into an IRC/sqlite3 compatible format
# 
# Copyright (c) 2015 Casey Bartlett <caseytb@bu.edu>
# 
# See LICENSE for terms of usage, modification and redistribution.

from bs4 import BeautifulSoup as bs
from urllib2 import urlopen, URLError
from collections import OrderedDict
from sopel import formatting
from string import Template
import exceptions
import datetime
import sqlite3
import copy
import sys
import re

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
    "Model":"model",
    "Model Number":"model_number",
    "Country of Origin":"country_of_origin",
    "Best Use":"usage",
    "Price":"price",
    "Vendor ID":"vendor_id",
    "Vendor Name":"vendor",
    "Date Added":"date_added"})

def replaceDictKeys(key_map, dict_to_change):
    d = dict()
    for k,v in key_map.iteritems():
        if k in dict_to_change:
            d[v] = dict_to_change[k]
    return d
def getSubDict(keys, theDict):
    d = dict()
    for k in keys:
        d[k] = theDict[k]

def checkTableExists(dbcon, tablename):
    """
    Database utility to check for existence of table
    """
    dbcur = dbcon.cursor()
    dbcur.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_name = '{0}'
        """.format(tablename.replace('\'', '\'\'')))
    if dbcur.fetchone()[0] == 1:
        dbcur.close()
        return True

    dbcur.close()
    return False

class inventoryDatabase:
    """
    Parse a page based on the first occurance of: <td colspan="4">
    """
    def __init__(self):
        self.foo = []
        self.database_file = "inventory.db"
        self.connection = []
        self.tablename = "blade_inventory"
        self.name_map = BHQNAME_TO_DBNAME
        # reindex so reverse lookups are possible
        d_copy = copy.deepcopy(self.name_map)
        for k,v in d_copy.iteritems():
            self.name_map[v] = k
        self.column_dict = INVENTORY_ITEMS 
        self.columns = self.column_dict.keys()
        self.open_database()

    def open_database(self):
        # Try connecting to the default database
        try:
            self.connection = sqlite3.connect(self.database_file)
        except sqlite3.Error as e:
            print("Error opening database. {}".format(e.args[0]))

    def _initialize_stdout(self, location):
        if location:
            sys.stdout = open(location,"w")

    def _get_SQLite_version(self):
        try:
            c = self.connection.cursor()
            c.execute('SELECT SQLITE_VERSION()')
            data = c.fetchone()
            return data
        except sqlite3.Error as e:
            print("Error getting SQLite version. {}".format(e.args[0]))

    def __del__(self):
        """
        Close the database connection when this object dies
        """
        if self.connection:
            self.connection.close()

    def create_db(self):    
        """
        Create the database. This is a standard layout
        TODO: generate this text from self.column_dict
        """
        self.connection.execute('''CREATE TABLE {table}
                (date_added text,
                overall_lengthMKS real,
                blade_lengthMKS real,
                cutting_edgeMKS real,
                blade_thicknessMKS real,
                blade_material text,
                blade_style text,
                blade_grind text,
                blade_finish text,
                handle_lengthMKS real,
                handle_thicknessMKS real,
                handle_material text,
                color text,
                frame_liner text,
                massMKS real,
                configuration text,
                clip_configurations text,
                knife_type text,
                open_type text,
                lock_type text,
                brand text,
                model text,
                model_number text,
                country_of_origin text,
                usage text,
                price real,
                vendor_id text PRIMARY KEY,
                vendor text)'''.format(table=self.tablename))

    def has_item(self,key,id):
        self.connection.execute("SELECT EXISTS(SELECT 1 FROM {table} WHERE {target}=\"{value}\" LIMIT 1);".format(table=self.tablename, target=key, value=id))
        cursor =self.connection.cursor()
        data = cursor.fetchall()
        print data
        return len(data) > 0

    def add_knife(self, knife_dict):
        """
        Adds a knife to the database. 
        @param: knife_dict is a dict of key value pairs following database format listed  in create_db(self)
        """
        key ="Vendor ID"
        if not knife_dict.has_key(key):
            print("No vendor_id found!")
        if self.has_item(self.name_map[key],knife_dict[key]):
            print("knife with {k} already in {tb}".format(k=key,tb=self.tablename))
            return
        ld = len(self.column_dict)
        knife_item = self._order_tuple(knife_dict)
        self.connection.execute("INSERT INTO {table} ".format(table=self.tablename)+"VALUES ({}{})".format("?,"*(ld-1),"?"), knife_item)
        self.connection.commit()

    def _order_tuple(self, knife_dict):
        """
        sqlite takes a tuple as the argument of the database so this function
        converts a dict into the appropriate key value paring
        """
        # an initially emptiy list
        insertion = []
        for k in self.column_dict.keys():
            if self.name_map.has_key(k):
                key = self.name_map[k]
                insertion.append(knife_dict[key])
            else:
                insertion.append(['NULL',])
        return tuple(insertion)

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
        vs = strip_units(v.text)
        key = k.text.strip(":")
        knife[key] = vs

    # Price - probably need to use price repr
    item_selection= soup.findAll("span",{"class": "item-descr-price"})
    price_element = item_selection[0].find("div", {"class" : "price" }).text
    price = parse_price_element(price_element)
    
    today = datetime.date.today()
    knife["Date Added"] = today.strftime(u"%x")
    knife["Vendor Name"] = u"BHQ"
    knife["Vendor ID"] = unicode(bhq_item_num)
    knife["Price"] = unicode(price) 
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
    print price_element
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
        fmt = Template("$model" +\
                " $blade_lengthMKS m blade length" +\
                " of $blade_material steel priced at [ $$" +\
                formatting.color("$price",fg=formatting.colors.GREEN)+\
                " ]")
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
    page = []
    #specValues = specs[0].findall('span', {"class":"attValue"})
    # Get the first table (this contains a huge list
    knife = query_test_knife()
    print knife
    #print(knife)
    #ib = inventoryDatabase()
    #ib.add_knife(knife)

# performs a test run where a database is created and a knife is added after parsing BHQ
def test_run():
    # Get this url with ddg search api
    query_string = "paramilitary 2"
    url= "http://www.bladehq.com/item--Spyderco-Paramilitary-2--7920"
    knife = query_bhq_knife(url)
    print "This is the knife:"
    print knife
    d = replaceDictKeys(BHQNAME_TO_DBNAME,knife)
    if knife:
        #ib = inventoryDatabase()
        #ib.add_knife(knife)
        kf = KnifeFormatter()
        print(kf.formattedKnife(d))
    else:
        print "I couldn't find the information {knife} but here's the first url I could find: {url}".format(knife = query_string,url=url)

if __name__ == '__main__':
    run()

