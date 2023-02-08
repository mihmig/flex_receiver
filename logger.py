# Простой логгер
from datetime import datetime
import sys


def log(line: str):
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), line)
    sys.stdout.flush()
