# Выгрузка трека из БД в формате GPX
# https://wiki.openstreetmap.org/wiki/RU:GPX (формат файла)
# https://www.mygpsfiles.com/app/ (вроде есть replay)
# https://gpx.studio/
# https://brouter.de/brouter-web/ (можно редактировать)
#

import json
import re
from config import config
from plugins.db_mysql import Db

db = Db(config['database'])

start = '2024-01-29 11:45:00'
end = '2024-01-29 12:25:00'
track_name = re.sub(r'[ :]', '-', (start + '_' + end))

records = db.get_data("SELECT `datetime`, decoded FROM message "
                      "WHERE device_id = 1 AND message_type = 'A' AND decoded IS NOT NULL AND datetime BETWEEN %s AND %s",
                      [start, end])

text_file = open(f"{track_name}.gpx", "w")
text_file.write(f'<?xml version="1.0" encoding="UTF-8"?>\n<gpx version="1.1" creator="flex_receiver">\n<name>{track_name}</name>\n')

start_wpt = json.loads(records[0].get('decoded'))
text_file.write(f'<wpt lat="{float(start_wpt.get("10"))/600000}" lon="{float(start_wpt.get("11"))/600000}">')
text_file.write(f'<name>{track_name}</name></wpt>\n<trk><number>1</number>\n\t<trkseg>\n')
# 10 Последняя валидная широта Угол широты, зафиксированный при получении последних валидных координат. В десятитысячных долях минуты.
# Например, 55° 42,2389' будет представлено как 33422389
# 11 Угол долготы, зафиксированный при получении последних валидных координат. В десятитысячных долях минуты.
# Например, 37° 41,6063' будет представлено как 22616063
# 12 Высота относительно уровня моря, зафиксированная при получении последних валидных координат: В дециметрах Например, 205 метров будет представлено как 2050 дециметров
# 13 Скорость, зафиксированная при получении последних валидных координат. В км/ч
# 14 Курс, зафиксированный при получении последних валидных координат.
for record in records:
    data = json.loads(record.get('decoded'))
    text_file.write(f'\t<trkpt lat="{float(data.get("10"))/600000}" lon="{float(data.get("11"))/600000}"><ele>{float(data.get("12"))/10}</ele></trkpt>\n')

text_file.write(f'</trkseg></trk></gpx>\n')
print('ok')