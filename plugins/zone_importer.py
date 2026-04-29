# Работа с геозонами: импорт, хранение, проверка на вхождение
import os
import xml.etree.ElementTree as ET

from plugins.storage import Storage


class ZoneImporter:
    def __init__(self, _storage: Storage):
        self.storage = _storage

    def import_from_axenta(self, kml_file_path: str, source: str = 'axenta') -> (bool, str):
        """
        Импортирует геозоны из файла
        :param kml_file_path: путь к файлу с геозонами в формате KML
        :param source: источник геозон для поля source в БД
        :return: статус загрузки и текст (ошибки или загрузки)
        """
        if not os.path.isfile(kml_file_path):
            return False, f'Файл не найден: {kml_file_path}'

        try:
            root = ET.parse(kml_file_path).getroot()
        except ET.ParseError as e:
            return False, f'Ошибка разбора XML/KML: {e}'
        except OSError as e:
            return False, f'Ошибка чтения файла: {e}'

        namespace = {'kml': 'http://www.opengis.net/kml/2.2'}
        placemarks = root.findall('.//kml:Placemark', namespace)

        if not placemarks:
            return False, 'В файле не найдено ни одной геозоны (Placemark)'

        imported_count = 0
        updated_count = 0
        deactivated_count = 0
        skipped_count = 0
        imported_names = set()
        type_mapping = {
            'circle': 'CIRCLE',
            'polygon': 'POLIGON',
            'line': 'LINE'
        }
        existed_zones = self.storage.get_data(
            "SELECT id, name FROM geo_zone WHERE source = %s",
            [source]
        )
        existed_by_name = {}
        for zone in existed_zones:
            existed_by_name.setdefault(zone['name'], []).append(zone['id'])

        for placemark in placemarks:
            name = (placemark.findtext('kml:name', default='', namespaces=namespace) or '').strip()
            tags = (placemark.findtext('kml:description', default='', namespaces=namespace) or '').strip()

            extended_data = placemark.find('kml:ExtendedData', namespace)
            source_geo = ''
            zone_type = ''
            radius = None
            if extended_data is not None:
                for data_tag in extended_data.findall('kml:Data', namespace):
                    data_name = (data_tag.get('name') or '').strip().lower()
                    data_value = (data_tag.findtext('kml:value', default='', namespaces=namespace) or '').strip()
                    if data_name == 'source_geo':
                        source_geo = data_value
                    elif data_name == 'type':
                        zone_type = type_mapping.get(data_value.lower(), '')
                    elif data_name == 'radius_circle':
                        radius = data_value

            if not name or not source_geo or not zone_type:
                skipped_count += 1
                continue

            imported_names.add(name)
            zone_data = {
                'name': name,
                'source': source,
                'tags': tags,
                'source_geo': source_geo,
                'radius': radius,
                'type': zone_type
            }

            zone_ids = existed_by_name.get(name, [])
            if not zone_ids:
                zone_data['enabled'] = True
                zone_data['alert'] = True
                self.storage.insert_dict('geo_zone', zone_data)
                imported_count += 1
                continue

            for zone_id in zone_ids:
                self.storage.execute(
                    """
                    UPDATE geo_zone
                    SET tags = %s,
                        source_geo = %s,
                        radius = %s,
                        type = %s,
                        enabled = true,
                        updated = NOW()
                    WHERE id = %s
                    """,
                    [tags, source_geo, radius, zone_type, zone_id]
                )
                updated_count += 1

        if imported_names:
            placeholders = ", ".join(["%s"] * len(imported_names))
            params = [source, *sorted(imported_names)]
            deactivated_count = self.storage.execute(
                f"UPDATE geo_zone SET enabled = false, updated = NOW() "
                f"WHERE source = %s AND name NOT IN ({placeholders}) AND enabled = true",
                params
            )
        else:
            deactivated_count = self.storage.execute(
                "UPDATE geo_zone SET enabled = false, updated = NOW() WHERE source = %s AND enabled = true",
                [source]
            )

        if imported_count == 0 and updated_count == 0:
            return False, f'Геозоны не импортированы: пропущено {skipped_count}'

        return True, (
            f'Импортировано: {imported_count}, обновлено: {updated_count}, '
            f'деактивировано: {deactivated_count}, пропущено: {skipped_count}'
        )
