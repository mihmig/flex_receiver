# Модуль взаимодействия с базой данных MySql (MariaDB)
from typing import List, Dict
from pymysql.cursors import DictCursor
import pymysqlpool


class Db:
    def __init__(self, config):
        self.pool = pymysqlpool.ConnectionPool(**config)

    # Получение одного значения
    def get_value(self, query: str, params: list = None) -> str | None:
        conn = self.pool.get_connection(pre_ping=True)
        cursor = conn.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return row[0] if row is not None else None

    # Получение одного кортежа
    def get_line(self, query: str, params: list = None) -> Dict:
        conn = self.pool.get_connection(pre_ping=True)
        cursor = conn.cursor(cursor=DictCursor)
        cursor.execute(query, params)
        row = cursor.fetchone()
        cursor.close()
        return row

    # Получение одного столбца
    def get_row(self, query: str, params: list = None) -> List:
        conn = self.pool.get_connection(pre_ping=True)
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        result = list()
        for row in rows:
            result.append(row[0])
        cursor.close()
        conn.close()
        return result

    # Получение словаря, где ключ - значения первого столбца, значения - значения второго столбца,
    # остальные столбцы игнорируются, например:
    # {'1' : 'aaa', '2': 'bbb'})
    def get_dict(self, query: str, params: list = None) -> dict | None:
        conn = self.pool.get_connection(pre_ping=True)
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = {}
        records = cursor.fetchall()
        for r in records:
            result[r[0]] = r[1]
        cursor.close()
        conn.close()
        return result

    # Получение списка строк, представленных словарём, например:
    # [{'id': 1, 'name': 'aaa'}, {'id': 2, 'name': 'aaa'}]
    def get_data(self, query: str, params: list = None) -> list[dict]:
        conn = self.pool.get_connection(pre_ping=True)
        cursor = conn.cursor(cursor=DictCursor)
        cursor.execute(query, params)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data

    # Выполнение произвольного запроса к БД (как правило - UPDATE)
    def execute(self, query: str, params: list = None) -> object:
        conn = self.pool.get_connection(pre_ping=True)
        cursor = conn.cursor()
        result = cursor.execute(query, params)
        cursor.close()
        cursor.close()
        conn.close()
        return result

    # Вставка данных, возвращает сгенерированный id
    def insert(self, query: str, params: list = None) -> int:
        conn = self.pool.get_connection(pre_ping=True)
        cursor = conn.cursor()
        cursor.execute(query, params)
        insert_id = cursor.connection.insert_id()
        cursor.close()
        conn.close()
        return insert_id
