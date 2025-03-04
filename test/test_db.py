import yaml

from plugins.db_mysql import Db

with open('config/config.yml', "r", encoding="utf-8") as stream:
    config = yaml.safe_load(stream)
db = Db(config['database'])
devices = db.get_data("SELECT * FROM device")
print(type(devices))
print(devices)

devices = db.get_dict("SELECT * FROM device")
print(type(devices))
print(devices)
