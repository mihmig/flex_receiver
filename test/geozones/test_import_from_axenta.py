import unittest

from plugins.zone_importer import ZoneImporter
from plugins.storage import Storage


class TestImportFromAxenta(unittest.TestCase):
    def test_import_from_axenta_success(self):
        storage = Storage()
        geo_zone = ZoneImporter(storage)

        # На случай, если предыдущий запуск оставил тестовые данные.
        storage.execute("DELETE FROM geo_zone WHERE source = %s", ['test'])
        try:
            ok, message = geo_zone.import_from_axenta('test/geozones/axenta.kml', source='test')
            self.assertTrue(ok)
            self.assertTrue(message.startswith('Импортировано геозон:'))

            count = storage.get_value("SELECT COUNT(*) FROM geo_zone WHERE source = %s", ['test'])
            self.assertEqual(12, count)

            first = storage.get_line(
                "SELECT * FROM geo_zone WHERE source = %s AND name = %s ORDER BY id ASC LIMIT 1",
                ['test', 'Трек-выезд']
            )
            self.assertIsNotNone(first)
            self.assertEqual('', first['tags'])
            self.assertEqual('LINE', first['type'])
            self.assertEqual('test', first['source'])
            self.assertTrue(first['source_geo'].startswith('[{"lat": 57.685741520454165'))

            third = storage.get_line(
                "SELECT * FROM geo_zone WHERE source = %s AND name = %s ORDER BY id ASC LIMIT 1",
                ['test', 'На курбу']
            )
            self.assertIsNotNone(third)
            self.assertEqual('#in_с_дачи,#out_на_дачу', third['tags'])
            self.assertEqual('POLIGON', third['type'])

            circle = storage.get_line(
                "SELECT * FROM geo_zone WHERE source = %s AND name = %s ORDER BY id ASC LIMIT 1",
                ['test', 'Город Любим']
            )
            self.assertIsNotNone(circle)
            self.assertEqual('CIRCLE', circle['type'])
        finally:
            # storage.execute("DELETE FROM geo_zone WHERE source = %s", ['test'])
            pass


if __name__ == '__main__':
    unittest.main()
