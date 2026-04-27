from dataclasses import dataclass

@dataclass
class GpsPoint:
    moment: str
    lon: float
    lat: float
    ele: float
    speed: float
