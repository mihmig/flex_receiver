import os
from plugins.db_mysql import Db


db = Db()
devices = db.get_dictionary("SELECT * FROM device")
print(type(devices))
print(devices)

