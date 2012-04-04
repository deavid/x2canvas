# encoding: UTF-8
from utils.whereami import realdir
import os, re
import os.path
# FileSystem Database driver...
# Simple wrapper that reads and writes confgurations in a fashion that bash can 
# easily read the values later.

class RowDoesNotExistError(Exception):
    "Exception triggered when trying to get a row which doesn't exist yet."

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

class TableWrapper(object):
    def __init__(self, database, table):
        setattr(database, table.__name__, self)
        self._db = database
        self._table = table(self._db.path)
        
    def create(self, **kwargs):
        row = self._table.create_row(data = kwargs, mode = "create")
        return row

    def upsert(self, **kwargs):
        row = self._table.create_row(data = kwargs, mode = "upsert")
        return row
        
    def read(self, **kwargs):
        try:
            row = self._table.create_row(data = kwargs, mode = "read")
            return row
        except RowDoesNotExistError:
            return None
        
    def default(self, **kwargs):
        row = self._table.create_row(data = kwargs, mode = "default")
        return row
        
    def items(self, **kwargs):
        iterator = self._table.items()
        return iterator
    
        
def dirname_sanitize(dirname):
    dirname = str(dirname).lower()
    if re.match("[0-9]",dirname[0]): dirname = "n" + dirname
    if re.match("[^\w]",dirname[0]): dirname = "o" + dirname
    dirname = re.sub('[^\w0-9]+','-',dirname)
    assert(re.match("^[\w\d]+$",dirname))
    return dirname

class Table(object):
    name = 'defaulttablename'
    fields = [
        # Field("fieldname", Types.String),
    ]
    key = [
        # '%(fieldname)s',
    ]
    _row_class = None

    def __init__(self, dbpath):
        self._path = realdir(dbpath, self.name)
        if not os.path.exists(self._path): os.mkdir(self._path)
        if not os.path.isdir(self._path): raise ValueError, "Path is not a directory"
    def path(self, *args):
        return os.path.join(self._path, *args)
        
    def create_row(self,data, mode):
        row = self._row_class(self, data = data, mode = mode)
        return row
        
    def items(self):
        for root, dirs, files in os.walk(self._path):
            if len(files) and not len(dirs):
                text_pk = os.path.relpath(root,self._path)
                pk = []
                while text_pk:
                    text_pk, tail = os.path.split(text_pk)
                    pk.append(tail)
                yield self._row_class(self, pk = pk, mode = "read")
        
    def pk(self, data):
        return [ dirname_sanitize(k % data) for k in self.key ]

class RowMetaclass(type):
    def __init__(cls, name, bases, dct):
        table = dct.get("_table_class",None)
        super(RowMetaclass, cls).__init__(name, bases, dct)
        if table:
            cls._initTable()

class Row(object):
    __metaclass__ = RowMetaclass
    _table_class = None
    
    @classmethod
    def _initTable(self):
        self._table_class._row_class = self
        for field in self._table_class.fields:
            fieldprop = property(lambda self: field.getrow(self), lambda self, value: field.setrow(self,value), lambda self: field.delrow(self))
            setattr(self, field.name, fieldprop)
    def __str__(self):
        return object.__str__(self).replace(" object "," " + "/".join(self._pk) + " ")
        
    def __init__(self, table, pk = None, data = None, mode = "create"):
        if pk is None:
            assert(data)
            pk = table.pk(data)
        else:
            assert(pk)
        self._pk = pk
        self._path = table.path(*pk)
        if data:
            if mode != "read" and not os.path.exists(self._path):
                os.makedirs( self._path )
            else:
                if mode == "create":
                    raise ValueError("Value %s already exists!" % repr(pk))
        if not os.path.isdir(self._path): 
            raise RowDoesNotExistError, "This row doesn't exist in the disk."
        self.table = table
        # Read table fields and setup properties for each one.
        if data:
            for field in self.table.fields:
                if field.name in data: 
                    if mode == "default":
                        if field.getrow(self) is not None:
                            del data[field.name]
                            continue
                    field.setrow(self, data[field.name])
                    del data[field.name]
        if data:
            print "WARN: The following data was not written:", data
            
    def delete(self):
        for field in self.table.fields:
            field.delrow(self)
        os.rmdir(self._path)
        
    def path(self, *args):
        return os.path.join(self._path, *args)


class Field(object):
    def __init__(self, name, datatype):
        self.name = name
        self.datatype = datatype
        
    def getrow(self, row):
        if os.path.exists(row.path(self.name)):
            return self.datatype.read(open(row.path(self.name)).read())
        else:
            return None
        
    def setrow(self, row, value):
        if value is None: self.delrow(row)
        else:
            open(row.path(self.name),"w").write(self.datatype.write(value))
        
    def delrow(self, row):
        os.unlink(row.path(self.name))
        
        
        
class BinaryType(object):
    @classmethod
    def read(cls, data):
        return data
        
    @classmethod
    def write(cls, data):
        return data

class StringType(object):
    @classmethod
    def read(cls, data):
        if data[-1] == "\n": return data[:-1]
        else: return data
        
    @classmethod
    def write(cls, data):
        return data + "\n"


class IntegerType(StringType):
    @classmethod
    def read(cls, data):
        data = StringType.read(data)
        return int(data)
        
    @classmethod
    def write(cls, data):
        data = "%d" % int(data)
        return StringType.write(data)
    
class Types(object):
    Binary = BinaryType
    Integer = IntegerType
    String = StringType
    
    
    
    
    

