#!/usr/bin/env python
from bs4 import BeautifulSoup as bs
from urllib2 import urlopen, URLError
import sqlite3
from collections import OrderedDict
import sys
import copy

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
        self.name_map = dict({
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
        # reindex so reverse lookups are possible
        d_copy = copy.deepcopy(self.name_map)
        for k,v in d_copy.iteritems():
            self.name_map[v] = k
        self.column_dict = OrderedDict([("date_added","text"),
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
        self.columns = self.column_dict.keys()

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
        self.connection.execute('''CREATE TABLE blade_inventory
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
                vendor_id text,
                vendor text)''')

    def add_knife(self, knife_dict):
        """
        Adds a knife to the database. 
        @param: knife_dict is a dict of key value pairs following database format listed  in create_db(self)
        """
        ld = len(self.column_dict)
        knife_item = self._order_tuple(knife_dict)
        #print knife_item
        #print len(knife_item)
        # A weird 
        self.connection.execute("INSERT INTO blade_inventory VALUES ({}{})".format("?,"*(ld-1),"?"), knife_item)
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
    
def run():
    page = []
    try:
        page = urlopen("{file_full_path}{file_name}".format(file_full_path='file:///home/casey/src/knife_scraper/html/',file_name='spyderco.html'))
    except URLError as e:
        print(e.reason)
    soup = bs(page)
    specs=soup.findAll('div', {'class':"prodSpecs tabContent show-this-tab"})
    specKeys = specs[0].findAll('span', {"class":"attName"})
    specValues = specs[0].findAll('span', {"class":"attValue"})
    Knife = OrderedDict()
    for k,v in zip(specKeys,specValues):
        vs = strip_units(v.text)
        key = k.text.strip(":")
        Knife[key] = vs
    # these attributes have to be pulled from somewhere else
    Knife["Date Added"] = "11/18/2015"
    Knife["Vendor Name"] = "BHQ"
    Knife["Vendor ID"] = 10801
    Knife["Price"] = 134.95
    #specValues = specs[0].findall('span', {"class":"attValue"})
    # Get the first table (this contains a huge list

if __name__ == '__main__':
    run()

