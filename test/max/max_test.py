from datetime import datetime

from plugins.max_sender import MaxSender
from plugins.storage import Storage

storage = Storage()
max_sender = MaxSender(storage)
max_sender.send_message(220733505, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
