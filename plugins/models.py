from dataclasses import dataclass
from datetime import datetime


@dataclass
class GpsPoint:
    moment: int
    lon: float
    lat: float
    ele: float
    speed: float

@dataclass
class ConvertRecordsResult:
    valid_points: list[GpsPoint]
    invalid_gps_records: int
    exported_points: int
    spoofed_points: int

class GpxFileInfo:
    filename: str
    full_path: str
    start: datetime
    end: datetime
    device_info: dict
    # Все точки за период
    valid_points: list[GpsPoint]
    # Точки, разбитые по сегментам (поездки)
    segments: list[list[GpsPoint]]
    invalid_gps_records: int
    exported_points: int
    spoofed_points: int
    gpx_track: str