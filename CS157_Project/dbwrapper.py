import psycopg2
import sys
from itertools import *


class DBwrapper:
    
    def __init__(self, conn_dict):
        self.database = conn_dict['database']
        self.dbuser = conn_dict['db_user']
        self.dbpass = conn_dict['db_pwd']
        self.dbhost = conn_dict['db_host']
        self.dbport = conn_dict['db_port']
        self.connection = None
    
    def connect(self):
        if self.connection:
            pass
        else:
            try:
                self.connection = psycopg2.connect(host = self.dbhost, 
                                                   port = self.dbport, 
                                                   database = self.database, 
                                                   user = self.dbuser, 
                                                   password = self.dbpass)
            except psycopg2.DatabaseError, e:
                print 'Error %s' % e
                sys.exit(1)
    
    def quit(self):
        if self.connection:
            self.connection.close()
    
    def do_query(self, query_string, to_dict=False):
        if self.connection:
            cur = self.connection.cursor()
            cur.execute(query_string)
            col_names = [desc[0] for desc in cur.description]
            while True:
                row = cur.fetchone()
                if row is None:
                    break
                if to_dict:
                    row_dict = dict(izip(col_names, row))
                    yield row_dict
                else:
                    yield row
            return
        
    def do_execute(self, sql_string):
        if self.connection:
            try:
                cur = self.connection.cursor()
                cur.execute(sql_string)
                self.connection.commit()
                return True
            except:
                return False
        return False
        


d = {'database': 'subDB', 
     'db_host': 'localhost', 
     'db_port': 5432,
     'db_user': 'seeker', 
     'db_pwd': 'fd821031'
     }

test = DBwrapper(d)
test.connect()
q_str = '''
        SELECT * FROM "testTable"
        '''
e_str = '''
        INSERT INTO "testTable"
        VALUES (98, 'test_execute')
        '''
test.do_execute(e_str)
result = test.do_query(q_str, True)
for r in result:
    print r['id'], r['name']

