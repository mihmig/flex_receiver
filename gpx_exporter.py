# Выгрузка трека из БД в формате GPX
# https://wiki.openstreetmap.org/wiki/RU:GPX (формат файла)
# https://www.mygpsfiles.com/app/ (вроде есть replay)
# https://gpx.studio/ (Можно в 3D, если выбрать картографическую подложку с поддержкой рельефа (например, OpenTopoMap или Mapbox)
# https://brouter.de/brouter-web/ (можно редактировать)
# https://gpxway.com/ (Просто посмотреть в 3D)
#

import json
import re
from datetime import datetime
from plugins.db_mysql import Db

from plugins.models import GpsPoint
from plugins.spoofing_zone_filter import SpoofingZoneFilter
from plugins.storage import Storage


def to_gpx_time(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%dT%H:%M:%SZ")
    if isinstance(value, str):
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"):
            try:
                dt = datetime.strptime(value, fmt)
                return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                continue
    return str(value)

def create_gps_track(_track_name: str, _track_points: list[GpsPoint]) -> str:
    track = [f'<?xml version="1.0" encoding="UTF-8"?>',
             f'<gpx version="1.1" creator="flex_receiver">',
             f'<trk><name>{_track_name}</name>',
             f'<trkseg>']
    for point in _track_points:
        track.append(f'\t<trkpt lat="{point.lat}" lon="{point.lon}">')
        track.append(f'\t\t<ele>{point.ele}</ele>')
        if point.moment:
            track.append(f'<time>{point.moment}</time>')
        if point.speed:
            track.append(f'<extensions><speed>{point.speed}</speed></extensions>')
        track.append(f'</trkpt>')
    track.append('</trkseg></trk></gpx>')
    return '\n'.join(track)

def save_gpx_track(track: str, _track_name: str):
    text_file = open(f"tracks/{_track_name}.gpx", "w")
    text_file.write(track)
    text_file.close()

storage = Storage()
spoofing_zone_filter = SpoofingZoneFilter(storage)

device_id = 9
device_info = storage.get_device(device_id)

start = '2026-04-29 00:00:00'
end = '2026-04-29 23:59:59'
# start = '2026-04-27 00:00:00'
# end = '2026-04-27 23:59:00'

track_name = f"{device_info['name']}_{re.sub(r'[ :]', '-', (start + '_' + end))}"

records = storage.get_device_messages(device_id, start, end)

# Фильтруем невалидные точки


exported_points = 0
dropped_points = 0

track_points: list[GpsPoint] = []
for record in records:
    data = json.loads(record.get('decoded'))
    lat = float(data.get("10"))/600000
    lon = float(data.get("11"))/600000

    if spoofing_zone_filter.point_in_spoofed_zone(lon, lat):
        # db.execute("DELETE FROM message WHERE id = %s", [record['id']])
        dropped_points += 1
        continue
    gps_point = GpsPoint(to_gpx_time(data.get("3")),
                         lon,
                         lat,
                         data.get("12") / 10,  # elevation
                         data.get("13") # speed
                         )

    track_points.append(gps_point)
    exported_points += 1
gps_track = create_gps_track(track_name, track_points)
save_gpx_track(gps_track, track_name)
print(f'Создан трек: {track_name}')
print(f'Экспортировано точек: {exported_points}')
print(f'Отброшено точек: {dropped_points}')
