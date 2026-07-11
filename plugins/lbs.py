# Загружаем примерные) координаты БС с сайта https://4cells.ru/
import argparse
import hashlib
import math
import time
from dataclasses import dataclass
from typing import Iterable
from urllib.parse import parse_qs, urlparse

import requests

from plugins.logger import log
from plugins.storage import Storage


API_BASE_URL = "https://4cells.ru:4444/api/map/enb"
DEFAULT_RADIAL_KM = 15.0
DEFAULT_TILE_KM = 3.0
DEFAULT_MCC_MNC = "250099"
DEFAULT_TECHS = ("gsm", "wcdma")
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
)


@dataclass
class TileBounds:
    lat_start: float
    lat_end: float
    lon_start: float
    lon_end: float


def parse_yandex_url(url: str) -> tuple[float, float]:
    """
    Возвращает (lat, lon) из yandex URL с параметром ll=lon,lat.
    """
    parsed = urlparse(url)
    ll = parse_qs(parsed.query).get("ll")
    if not ll:
        raise ValueError("В URL не найден параметр ll=lon,lat")

    raw_parts = ll[0].split(",")
    if len(raw_parts) != 2:
        raise ValueError("Некорректный формат ll в URL, ожидается ll=lon,lat")

    lon = float(raw_parts[0])
    lat = float(raw_parts[1])
    return lat, lon


def km_to_lat_degrees(km: float) -> float:
    return km / 111.32


def km_to_lon_degrees(km: float, latitude: float) -> float:
    return km / (111.32 * math.cos(math.radians(latitude)))


def build_tiles(center_lat: float, center_lon: float, radius_km: float, tile_km: float) -> list[TileBounds]:
    """
    Строит квадраты tile_km x tile_km для покрытия окружности radius_km.
    """
    min_lat = center_lat - km_to_lat_degrees(radius_km)
    max_lat = center_lat + km_to_lat_degrees(radius_km)
    min_lon = center_lon - km_to_lon_degrees(radius_km, center_lat)
    max_lon = center_lon + km_to_lon_degrees(radius_km, center_lat)

    step_lat = km_to_lat_degrees(tile_km)
    step_lon = km_to_lon_degrees(tile_km, center_lat)

    lat_steps = max(1, math.ceil((max_lat - min_lat) / step_lat))
    lon_steps = max(1, math.ceil((max_lon - min_lon) / step_lon))

    tiles: list[TileBounds] = []
    for lat_idx in range(lat_steps):
        lat_start = min_lat + lat_idx * step_lat
        lat_end = min(max_lat, lat_start + step_lat)
        for lon_idx in range(lon_steps):
            lon_start = min_lon + lon_idx * step_lon
            lon_end = min(max_lon, lon_start + step_lon)
            tiles.append(
                TileBounds(
                    lat_start=lat_start,
                    lat_end=lat_end,
                    lon_start=lon_start,
                    lon_end=lon_end,
                )
            )
    return tiles


def make_request_id(seed: str) -> str:
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


class LbsLoader:
    def __init__(self, storage: Storage, mcc_mnc: str):
        self.storage = storage
        self.mcc_mnc = mcc_mnc
        self.session = requests.Session()
        self.session.headers.update(
            {
                "accept": "application/json, text/plain, */*",
                "origin": "https://4cells.ru",
                "referer": "https://4cells.ru/",
                "user-agent": USER_AGENT,
            }
        )

    def fetch_stations(self, tech: str, tile: TileBounds, request_index: int) -> list[dict]:
        url = f"{API_BASE_URL}/{tech}/{self.mcc_mnc}"
        params = {
            "latStart": f"{tile.lat_start:.12f}",
            "latEnd": f"{tile.lat_end:.12f}",
            "lonStart": f"{tile.lon_start:.12f}",
            "lonEnd": f"{tile.lon_end:.12f}",
        }
        request_id = make_request_id(
            f"{tech}:{request_index}:{params['latStart']}:{params['latEnd']}:{params['lonStart']}:{params['lonEnd']}:{time.time_ns()}"
        )
        log(f'downloading {url}/{params}')
        response = self.session.get(
            url,
            params=params,
            headers={"x-request-id": request_id},
            timeout=20,
        )
        response.raise_for_status()

        payload = response.json()
        if not isinstance(payload, list):
            raise ValueError(f"Ожидался список станций, получен тип: {type(payload)}")
        return payload

    def load(
        self,
        center_lat: float,
        center_lon: float,
        radius_km: float,
        tile_km: float,
        techs: Iterable[str],
        delay_seconds: float = 0.0,
    ) -> dict:
        tiles = build_tiles(center_lat, center_lon, radius_km, tile_km)
        unique_stations: dict[int, dict] = {}
        errors = 0
        total_requests = 0

        log(
            f"LBS: center=({center_lat:.6f}, {center_lon:.6f}) radius={radius_km}km "
            f"tile={tile_km}km tiles={len(tiles)} techs={','.join(techs)}"
        )

        for tile_idx, tile in enumerate(tiles, start=1):
            for tech in techs:
                total_requests += 1
                try:
                    rows = self.fetch_stations(tech, tile, total_requests)
                except Exception as e:
                    errors += 1
                    log(
                        f"LBS: request error tech={tech} tile={tile_idx}/{len(tiles)} "
                        f"lat={tile.lat_start:.5f}-{tile.lat_end:.5f} "
                        f"lon={tile.lon_start:.5f}-{tile.lon_end:.5f}: {e}"
                    )
                    continue

                for row in rows:
                    if "id" not in row:
                        continue
                    row["valid"] = True
                    unique_stations[row["id"]] = row

                if delay_seconds > 0:
                    time.sleep(delay_seconds)

        saved_count = self.storage.upsert_lbs_stations(list(unique_stations.values()))
        result = {
            "requests": total_requests,
            "errors": errors,
            "unique_stations": len(unique_stations),
            "saved": saved_count,
        }
        log(
            f"LBS: completed requests={result['requests']} errors={result['errors']} "
            f"stations={result['unique_stations']} saved={result['saved']}"
        )
        return result


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Загрузка базовых станций 2G/3G из 4cells")
    parser.add_argument("--url", required=True, help="Ссылка на карту Яндекс с параметром ll=lon,lat")
    parser.add_argument("--radius-km", type=float, default=DEFAULT_RADIAL_KM, help="Радиус поиска в км")
    parser.add_argument("--tile-km", type=float, default=DEFAULT_TILE_KM, help="Размер квадрата запроса в км")
    parser.add_argument("--mcc-mnc", default=DEFAULT_MCC_MNC, help="Код сети, например 250099")
    parser.add_argument(
        "--techs",
        default=",".join(DEFAULT_TECHS),
        help="Список технологий через запятую, например gsm,wcdma",
    )
    parser.add_argument("--delay-seconds", type=float, default=0.0, help="Пауза между запросами")
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    center_lat, center_lon = parse_yandex_url(args.url)
    techs = tuple(t.strip().lower() for t in args.techs.split(",") if t.strip())

    if not techs:
        raise ValueError("Не указаны технологии для загрузки")

    storage = Storage()
    loader = LbsLoader(storage=storage, mcc_mnc=args.mcc_mnc)
    loader.load(
        center_lat=center_lat,
        center_lon=center_lon,
        radius_km=args.radius_km,
        tile_km=args.tile_km,
        techs=techs,
        delay_seconds=max(0.0, args.delay_seconds),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
