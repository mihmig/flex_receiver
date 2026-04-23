# Модуль взаимодействия с базой данных MySql (MariaDB)
import os
from typing import List, Dict

from contextlib import contextmanager
from pymysql.cursors import DictCursor
import pymysqlpool


class Db:
    def __init__(self, config = None):
        if config is None:
            self.pool = pymysqlpool.ConnectionPool(**{
            'host': os.environ['DATABASE_HOST'],
            'port': int(os.environ['DATABASE_PORT']),
            'database': os.environ['DATABASE_NAME'],
            'user': os.environ['DATABASE_USER'],
            'password': os.environ['DATABASE_PASSWORD'],
            'autocommit': True,
            'size': 3,
            'maxsize': 5,
            'pre_create_num': 3,
            'name': 'pool1',
            'charset': 'utf8mb4'
        })
        else:
            self.pool = pymysqlpool.ConnectionPool(**config)

    @contextmanager
    def connection(self):
        conn = self.pool.get_connection(pre_ping=True)
        try:
            yield conn
        finally:
            conn.close()

    def get_value(self, query: str, params: list = None) -> str | None:
        """ Получение одного значения """
        with self.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                row = cursor.fetchone()
                return row[0] if row is not None else None

    def get_line(self, query: str, params: list = None) -> Dict:
        """ Получение одного кортежа """
        conn = self.pool.get_connection(pre_ping=True)
        cursor = conn.cursor(cursor=DictCursor)
        cursor.execute(query, params)
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return row

    def get_row(self, query: str, params: list = None) -> List:
        """ Получение одного столбца """
        with self.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
                return [row[0] for row in rows]


    def get_dict(self, query: str, params: list = None) -> dict | None:
        """
        Получение словаря, где ключ - значения первого столбца, значения - значения второго столбца,
        остальные столбцы игнорируются, например:
        # {'1' : 'aaa', '2': 'bbb'}
        :param query:  SQL-выражение
        :param params: параметры
        :return:  словарь
        """
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

    def get_data(self, query: str, params: list = None) -> list[dict]:
        """
        Получение списка кортежей
        :param query:  SQL-выражение
        :param params: параметры
        :return: список кортежей
        """
        with self.connection() as conn:
            with conn.cursor(cursor=DictCursor) as cursor:
                cursor.execute(query, params)
                return list(cursor.fetchall())

    def get_dictionary(self, query: str, params: list = None) -> dict[dict]:
        """
        Получение списка кортежей в виде словаря словарей. Ключ - первый стобец запроса
        :param query:  SQL-выражение
        :param params: параметры
        :return: список кортежей
        """
        with self.connection() as conn:
            with conn.cursor(cursor=DictCursor) as cursor:
                cursor.execute(query, params)
                data = cursor.fetchall()

        if not data:
            return {}

        # Получаем имя первого столбца — берём ключи первого элемента, берём первый ключ
        first_column_name = next(iter(data[0].keys()))

        return {
            row[first_column_name]: row
            for row in data
        }

    def execute(self, query: str, params: list = None):
        """
        Выполнение произвольного запроса к БД
        :param query:  SQL-выражение
        :param params: параметры
        :return:
        """
        with self.connection() as conn:
            with conn.cursor(cursor=DictCursor) as cursor:
                return cursor.execute(query, params)

    def insert(self, query: str, params: list = None) -> int:
        """
        Вставка данных, возвращает сгенерированный id
        :param query:  SQL-выражение
        :param params: параметры
        :return:       сгенерированный id
        """
        with self.connection() as conn:
            with conn.cursor(cursor=DictCursor) as cursor:
                cursor.execute(query, params)
                return conn.insert_id()

    def insert_dict(self, table: str, data: dict) -> int:
        """
        Универсальная вставка словаря в таблицу.
        Ключи словаря должны совпадать с именами столбцов.
        :param table: таблица БД
        :param data:  словарь с данными
        :return:      сгенерированный id
        """
        # Формируем список имен столбцов и заглушек %s
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))

        # Собираем итоговый SQL
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        with self.connection() as conn:
            with conn.cursor(cursor=DictCursor) as cursor:
                # Передаем значения словаря в правильном порядке
                cursor.execute(query, list(data.values()))
                return conn.insert_id()
