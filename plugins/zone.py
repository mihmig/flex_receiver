# Геозоны
from shapely.geometry import Polygon


class Zone:
    id: int
    parent_id: int
    type: str
    name: str
    tags: str
    alert: bool

class CircleZone(Zone):
    lat: float
    lon: float
    radius: float

class PolygonZone(Zone):
    polygon: Polygon
