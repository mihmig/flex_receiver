from plugins.db_mysql import Db

db = Db()
devices = db.get_data("SELECT * FROM device")
print(type(devices))
print(devices)

devices = db.get_dict("SELECT * FROM device")
print(type(devices))
print(devices)
