#!/usr/bin/env python
# bhq_inventory_database.py - Database functions to access
# 
# Copyright (c) 2015,2016 Casey Bartlett <caseytb@bu.edu>
# 
# See LICENSE for terms of usage, modification and redistribution.

import sqlite3
from bhq_inventory_items import INVENTORY_ITEMS, BHQNAME_TO_DBNAME 
import copy
import sys


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
                url text,
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

def run():
    #specValues = specs[0].findall('span', {"class":"attValue"})
    # Get the first table (this contains a huge list
    #knife = query_test_knife()
    #print knife
    #print(knife)
    ib = inventoryDatabase()
    #ib.add_knife(knife)

if __name__ == '__main__':
    run()
