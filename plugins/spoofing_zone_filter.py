# Фильтрация координат при спуфинге GPS-сигнала
import json

from geopy.distance import great_circle
from shapely.geometry import Point, Polygon

from plugins.storage import Storage
from plugins.zone import CircleZone, PolygonZone


class SpoofingZoneFilter:
    def __init__(self, _storage: Storage):
        self.storage = _storage
        self.active_geo_zones = self.storage.get_active_geo_zones()
        self.polygon_zones: list[Polygon] = []
        self.circle_zones: list[CircleZone] = []

        for geo_zone in self.active_geo_zones:
            if not geo_zone['name'].startswith('spoof'):
                continue
            if geo_zone['type'] == 'CIRCLE':
                cz = CircleZone()
                cz.id = geo_zone['id']
                cz.type = geo_zone['type']
                cz.name = geo_zone['name']
                cz.tags = geo_zone['tags']
                cz.alert = geo_zone['alert']
                cz.radius = geo_zone['radius']
                center: dict = json.loads(geo_zone['source_geo'])
                cz.lat = center['lat']
                cz.log = center['log']
                self.circle_zones.append(cz)
            elif geo_zone['type'] == 'POLIGON':
                pz = PolygonZone()
                pz.id = geo_zone['id']
                pz.type = geo_zone['type']
                pz.name = geo_zone['name']
                pz.tags = geo_zone['tags']
                pz.alert = geo_zone['alert']
                pz.polygon = self._source_geo_to_polygon(geo_zone['source_geo'])
                self.polygon_zones.append(pz)

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
        in_polygon = any(polygon.covers(point) for polygon in self.polygon_zones)
        if in_polygon:
            return True

        return any(
            self._point_in_circle(_lon, _lat, zone["lon"], zone["lat"], zone["radius"])
            for zone in self.circle_zones
        )