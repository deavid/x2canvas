# encoding: UTF-8
import sys, os.path
import utils.whereami
import utils.fsdb
import dbscheme

DATABASE = '../data'
dbTemplate = utils.fsdb.DatabaseTemplate(dbscheme)

db = dbTemplate.connect(DATABASE)

admin_user = db.Users.create(name="admin")


db.close()


