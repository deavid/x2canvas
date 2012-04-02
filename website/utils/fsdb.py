# encoding: UTF-8
from utils.whereami import realdir
import os
import os.path
# FileSystem Database driver...
# Simple wrapper that reads and writes confgurations in a fashion that bash can 
# easily read the values later.

class DatabaseTemplate(object):
    def __init__(self, Schema):
        # Clone the schema
        self.tables = [ obj for k,obj in Schema.__dict__.items() if type(obj) is type(Table) and issubclass(obj,Table) and obj != Table]
        
    def connect(self, path):
        db = Database(self, path)
        return db
        
    
    

class Database(DatabaseTemplate):
    def __init__(self, template, path):
        self.tables = template.tables
        self.path = path
        for table in self.tables:
            TableWrapper(self, table)

    def close(self):
        "Close Database, shutdown any open resource."        
        return
        
    def new_row(self, table, data):
        row = table(self.path)
        row.create_row(data)

class TableWrapper(object):
    def __init__(self, database, table):
        setattr(database, table.__name__, self)
        self._db = database
        self._table = table
        
    def create(self, **kwargs):
        row = self._db.new_row(self._table, data = kwargs)
        

class Table(object):
    def __init__(self, dbpath):
        self._path = realdir(dbpath, self.name)
        if not os.path.isdir(self._path): raise ValueError, "Path is not a directory"
    def path(self, *args):
        return os.path.join(self._path, *args)
        
    def create_row(self,data):
        pk = self.pk(data)
        rowpath = self.path(*pk)
        if not os.path.exists(rowpath):
            os.makedirs( rowpath )
            
        row = Row(self, rowpath)
        row._pk = pk
        row._data = data
        
    def pk(self, data):
        return [ k % data for k in self.key ]

class Row(object):
    def __init__(self, table, rowpath):
        self._path = rowpath
        if not os.path.isdir(self._path): raise ValueError, "Path is not a directory"
        # TODO: Read table fields and setup properties for each one.


class Field(object):
    def __init__(self, name, datatype):
        self.name = name
        self.datatype = datatype

    
class Types(object):
    Integer = int
    String = str
    
    
    
    
    

