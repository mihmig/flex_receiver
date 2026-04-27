# Фильтрация координат при спуфинге GPS-сигнала
from plugins.db_mysql import Db
from shapely.geometry import Point, Polygon

class SpoofingZoneFilter:
    def __init__(self,db: Db):
        self.db = db
        self.poligones = [
            ]
        spoofing_zone = [
            {"lat": 57.72690736886437, "lng": 39.91058349609375},
            {"lat": 57.72709103965814, "lng": 40.04911422729492},
            {"lat": 57.6685445544838, "lng": 40.05134582519532},
            {"lat": 57.667808672736825, "lng": 39.91127014160156},
            {"lat": 57.72690736886437, "lng": 39.91058349609375}  # замыкающая точка
        ]
        # 1️⃣ Преобразуем в формат shapely: [(lng, lat), ...]
        shapely_coords = [(p["lng"], p["lat"]) for p in spoofing_zone]
        # Добавляем полигон (последнюю дублирующую точку можно оставить или убрать: shapely_coords[:-1])
        self.poligones.append(Polygon(shapely_coords[:-1]))

    def point_in_spoofed_zone(self, _lon: float, _lat: float) -> bool:
        """
        Проверяет - находится ли точка в зоне спуфинга GPS
        :param _lon: долгота
        :param _lat: широта
        :return: True - если находится, False - если нет
        """
        point = Point(_lon, _lat)
        return any(polygon.covers(point) for polygon in self.poligones)