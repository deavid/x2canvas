# encoding: UTF-8
import sys, os.path
import utils.whereami
import utils.fsdb
import dbscheme

DATABASE = '../data'
dbTemplate = utils.fsdb.DatabaseTemplate(dbscheme)

db = dbTemplate.connect(DATABASE)

admin_user = db.Users.default(name="admin", password="password")
print admin_user
for user in db.Users.items():
    print user
print db.Users.read(name="user1")
db.close()


