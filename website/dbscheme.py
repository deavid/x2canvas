# encoding: UTF-8
from utils.fsdb import Table, Field, Types, Row

class ListeningPorts(Table):
    name = 'listening_ports'
    fields = [
        Field("port_number", Types.Integer),
    ]
    key = [
        'listen-%(port_number)d'
    ]

class ListeningPort(Row):
    _table_class = ListeningPorts


# Sessions

# Users
class Users(Table):
    name = 'users'
    fields = [
        Field("name", Types.String),
        Field("password", Types.String),
    ]
    key = [
        '%(name)s'
    ]

class User(Row):
    _table_class = Users



class Properties(Table):
    name = 'properties'
    fields = [
        Field("name", Types.String),
        Field("value", Types.String),
    ]
    key = [
        'key-%(name)s'
    ]

class Property(Row):
    _table_class = Properties


