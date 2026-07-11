# Контроль входа и выхода из геозон
# Фильтрация координат при спуфинге GPS-сигнала
import json

from geopy.distance import great_circle
from shapely.geometry import Point, Polygon

from plugins.storage import Storage
from plugins.zone import CircleZone, PolygonZone, Zone


class GeofenceService:
    def __init__(self, _storage: Storage):
        self.storage = _storage
        self.geofences = self.storage.get_geofences()
        # Обычные зоны
        self.zones: dict[int, Zone] = {}
        # Зоны спуфигна GPS
        self.spoofing_zones: list[Zone] = []

        self.spoofing_polygon_zones: list[PolygonZone] = []
        self.spoofing_circle_zones: list[CircleZone] = []

        # Конвертируем зоны из БД
        zones: list[Zone] = []
        for geofence in self.geofences:
            zone: Zone = self._get_zone(geofence)
            if zone is None:
                continue
            if geofence['name'].startswith('spoof'):
                self.spoofing_zones.append(zone)
                continue
            zones.append(zone)

        zone_by_id: dict[int, Zone] = {z.id: z for z in zones}
        self.zones = zone_by_id

        roots: list[Zone] = []
        for z in zones:
            pid = z.parent_id or 0
            if pid and pid in zone_by_id:
                zone_by_id[pid].childrens.append(z)
            else:
                roots.append(z)

        for z in roots:
            if isinstance(z, PolygonZone):
                self.spoofing_polygon_zones.append(z)
            elif isinstance(z, CircleZone):
                self.spoofing_circle_zones.append(z)

    def _get_zone(self, db_item: dict) -> Zone|None:
        if db_item['type'] == 'CIRCLE':
            cz = CircleZone()
            cz.id = db_item['id']
            cz.parent_id = db_item.get('parent_id') or 0
            cz.childrens = []
            cz.type = db_item['type']
            cz.name = db_item['name']
            cz.tags = db_item['tags']
            cz.alert = db_item['alert']
            cz.radius = db_item['radius']
            center: dict = json.loads(db_item['source_geo'])
            cz.lat = center['lat']
            cz.lon = center.get('lng', center.get('log', 0.0))
            return cz
        if db_item['type'] == 'POLIGON':
            pz = PolygonZone()
            pz.id = db_item['id']
            pz.parent_id = db_item.get('parent_id') or 0
            pz.childrens = []
            pz.type = db_item['type']
            pz.name = db_item['name']
            pz.tags = db_item['tags']
            pz.alert = db_item['alert']
            pz.polygon = self._source_geo_to_polygon(db_item['source_geo'])
            return pz
        return None

    @staticmethod
    def _source_geo_to_polygon(source_geo: str) -> Polygon:
        points = json.loads(source_geo)
        polygon_coords = [(p["lng"], p["lat"]) for p in points]
        return Polygon(polygon_coords[:-1])

    @staticmethod
    def _point_in_circle(lon: float, lat: float, center_lon: float, center_lat: float, radius: float) -> bool:
        # geopy принимает координаты в формате (lat, lon)
        distance = great_circle((lat, lon), (center_lat, center_lon)).m
        return distance <= radius

    def point_in_spoofed_zone(self, _lon: float, _lat: float) -> bool:
        """
        Проверяет - находится ли точка в зоне спуфинга GPS
        :param _lon: долгота
        :param _lat: широта
        :return: True - если находится, False - если нет
        """
        point = Point(_lon, _lat)
        in_polygon = any(
            polygon_zone.polygon.covers(point) for polygon_zone in self.spoofing_polygon_zones
        )
        if in_polygon:
            return True

        return any(
            self._point_in_circle(_lon, _lat, zone.lon, zone.lat, zone.radius)
            for zone in self.spoofing_circle_zones
        )
if __name__ == '__main__':
    storage = Storage()
    geofence_service = GeofenceService(storage)
    print('Импортировано геозон:')
    print(f'Spoofed: {len(geofence_service.spoofing_zones)}')
    print(f'Polygon: {len(geofence_service.spoofing_polygon_zones)}')
    print(f'Circle: {len(geofence_service.spoofing_circle_zones)}')