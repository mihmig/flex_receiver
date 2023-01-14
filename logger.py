# Простой логгер
from datetime import datetime


def log(line: str):
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), line)
