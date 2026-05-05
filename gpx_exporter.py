# Выгрузка трека из БД в формате GPX
# https://wiki.openstreetmap.org/wiki/RU:GPX (формат файла)
# https://www.mygpsfiles.com/app/ (вроде есть replay)
# https://gpx.studio/ (Можно в 3D, если выбрать картографическую подложку с поддержкой рельефа (например, OpenTopoMap или Mapbox)
# https://brouter.de/brouter-web/ (можно редактировать)
# https://gpxway.com/ (Просто посмотреть в 3D)
#

import json
import math
import re
from datetime import datetime

from plugins.models import GpsPoint, GpxFileInfo, ConvertRecordsResult
from plugins.spoofing_zone_filter import SpoofingZoneFilter
from plugins.storage import Storage

class GpxExporter():
    def __init__(self,
                 p_storage: Storage,
                 p_spoofing_zone_filter: SpoofingZoneFilter,
                 p_tracks_folder: str = 'tracks'):
        self.storage = p_storage
        self.spoofing_zone_filter = p_spoofing_zone_filter
        self.tracks_folder = p_tracks_folder

    @staticmethod
    def to_gpx_time(value: int) -> str:
        return datetime.fromtimestamp(value).strftime('%Y-%m-%d %H:%M:%SZ')

    @staticmethod
    def date_from_str(value: str) -> datetime:
        for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        raise Exception(f"Некорректный формат даты:{value}")

    def get_time_range(self,
                       p_from: str|datetime|None = None,
                       p_to: str|datetime|None = None) -> (datetime, datetime):
        if p_from is None:
            start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end = start.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif isinstance(p_from, str):
            start = self.date_from_str(p_from)
            if p_to is None:
                end = start.replace(hour=23, minute=59, second=59, microsecond=999999)
            else:
                end = self.date_from_str(p_to)
        else:
            start = p_from
            if p_to is None:
                end = start.replace(hour=23, minute=59, second=59, microsecond=999999)
            else:
                end = p_to
        return start, end

    @staticmethod
    def distance_meters(first: GpsPoint, second: GpsPoint) -> float:
        # Haversine distance between two WGS84 points.
        earth_radius_m = 6371000
        lat1 = math.radians(first.lat)
        lat2 = math.radians(second.lat)
        delta_lat = math.radians(second.lat - first.lat)
        delta_lon = math.radians(second.lon - first.lon)
        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return earth_radius_m * c


    @staticmethod
    def convert_records(p_records: list[dict]) -> ConvertRecordsResult:
        invalid_gps = 0
        exported = 0
        spoofed = 0

        valid_points: list[GpsPoint] = []
        for record in p_records:
            data = json.loads(record.get('decoded'))

            # Фильтруем невалидные точки
            if not data.get('8', 0) & 2:  # Невалидная навигация
                invalid_gps += 1
                continue
            # Последние валидные координаты были более 10 секунд назад
            if data.get('3', 100) - data.get('9', 0) > 10:
                invalid_gps += 1
                continue
            lat = float(data.get("10")) / 600000
            lon = float(data.get("11")) / 600000
            # Точка в spoofing-зоне
            if spoofing_zone_filter.point_in_spoofed_zone(lon, lat):
                # db.execute("DELETE FROM message WHERE id = %s", [record['id']])
                spoofed += 1
                continue
            gps_point = GpsPoint(data.get("3"),  # Или 9 ?
                                 lon,
                                 lat,
                                 data.get("12") / 10,  # elevation
                                 data.get("13")  # speed
                                 )
            valid_points.append(gps_point)
            exported += 1
        return ConvertRecordsResult(
            valid_points,
            invalid_gps,
            exported,
            invalid_gps
        )

    def split_track_to_segments(self,
         _track_points: list[GpsPoint],
         max_distance_m: float = 500,
         max_gap: int = 300
         ) -> list[list[GpsPoint]]:
        if not _track_points:
            return []
        segments: list[list[GpsPoint]] = [[_track_points[0]]]
        for current in _track_points[1:]:
            previous = segments[-1][-1]
            # Если:
            # 1. Следующая точка отстоит от текщей более чем на 500 метров
            # или
            # 2. Между точками прошло более чем 5 минут
            # То начинаем новый сегмент трека
            gap_exceeded = (current.moment - previous.moment) > max_gap
            distance_exceeded = self.distance_meters(previous, current) > max_distance_m
            if gap_exceeded or distance_exceeded:
                segments.append([current])
            else:
                segments[-1].append(current)
        return segments

    #
    # def filter_segments(self, segments: list[list[GpsPoint]]) -> list[list[GpsPoint]]:
    #     return segments

    def create_gps_track(self,
                         p_track_name: str,
                         segments: list[list[GpsPoint]]) -> str:
        track = [f'<?xml version="1.0" encoding="UTF-8"?>',
                 f'<gpx version="1.1" creator="flex_receiver">',
                 f'<trk><name>{p_track_name}</name>']

        for segment in segments:
            track.append(f'<trkseg>')
            for point in segment:
                track.append(f'\t<trkpt lat="{point.lat}" lon="{point.lon}">')
                track.append(f'\t<ele>{point.ele}</ele>')
                if point.moment:
                    track.append(f'\t<time>{self.to_gpx_time(point.moment)}</time>')
                if point.speed:
                    track.append(f'\t<extensions><speed>{point.speed}</speed></extensions>')
                track.append(f'</trkpt>')
            track.append('</trkseg>')
        track.append('</trk></gpx>')
        return '\n'.join(track)

    def save_to_gpx(self, track: str, p_track_file_name: str):
        full_path = f"{self.tracks_folder}/{p_track_file_name}.gpx"
        text_file = open(full_path, "w")
        text_file.write(track)
        text_file.close()
        return full_path

    def create_gpx_file(self,
                        p_device_id: int,
                        p_from: str|datetime|None = None,
                        p_to: str|datetime|None = None) -> GpxFileInfo:

        _gpx_file_info = GpxFileInfo()
        device_info = self.storage.get_device(p_device_id)
        _gpx_file_info.device_info = device_info

        start, end = self.get_time_range(p_from, p_to)
        _gpx_file_info.start = start
        _gpx_file_info.end = end

        records: list[dict] = storage.get_device_messages(p_device_id, start, end)
        convert_records_result: ConvertRecordsResult = self.convert_records(records)
        _gpx_file_info.valid_points = convert_records_result.valid_points
        _gpx_file_info.invalid_gps_records = convert_records_result.invalid_gps_records
        _gpx_file_info.exported_points = convert_records_result.exported_points
        _gpx_file_info.spoofed_points = convert_records_result.spoofed_points

        _gpx_file_info.segments = self.split_track_to_segments(_gpx_file_info.valid_points)

        filename = f"{device_info['name']}_{start.strftime('%Y-%m-%d %H:%M:%S')}_{end.strftime('%Y-%m-%d %H:%M:%S')}"
        filename = re.sub(r'[ :]', '-', filename)
        _gpx_file_info.name = filename

        _gpx_file_info.gpx_track = self.create_gps_track(_gpx_file_info.name, _gpx_file_info.segments)
        _gpx_file_info.full_path = self.save_to_gpx(_gpx_file_info.gpx_track, filename)
        return _gpx_file_info


if __name__ == '__main__':
    device_id = 1
    date = '2026-05-04'

    storage = Storage()
    spoofing_zone_filter = SpoofingZoneFilter(storage)
    gpx_exporter = GpxExporter(storage, spoofing_zone_filter)
    gpx_file_info: GpxFileInfo = gpx_exporter.create_gpx_file(device_id, date)
    print(f'Создан трек: {gpx_file_info.full_path}')
    print(f'Точек с невалидной навигацией: {gpx_file_info.invalid_gps_records}')
    print(f'Экспортировано точек: {gpx_file_info.exported_points}')
    print(f'Отброшено точек (спуффинг): {gpx_file_info.spoofed_points}')

