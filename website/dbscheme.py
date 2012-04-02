# encoding: UTF-8
from utils.fsdb import Table, Field, Types

class ListeningPorts(Table):
    name = 'listening_ports'
    fields = [
        Field("port_number", Types.Integer),
    ]
    key = [
        '%(port_number)d'
    ]


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


