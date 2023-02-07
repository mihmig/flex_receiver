# Тестирование отправки сообщения ботом
import os
import requests
from telegram import Sender
from config import config

chat_id = -1001882219961 # Inside оповещения

sender = Sender(config['telegram'])
sender.send_message(chat_id, "Проверка отправки сообщений")