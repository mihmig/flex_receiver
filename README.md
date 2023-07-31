## Приём телеметрии с GNSS-трекеров по протоколу FLEX

### Установка
* Установка зависимостей (библиотек python)
  pip install -r requirements.txt
* Загрузка справочников:
* MariaDB (MySql):
    ``` bash
    mysqlimport --local --fields-terminated-by=";" --lines-terminated-by="\r\n" -d -v gnss event.csv
    mysqlimport --local --fields-terminated-by=";" --lines-terminated-by="\r\n" -d -v gnss parameter.csv
    ```

### Документация к трекеру
* https://www.navtelecom.ru/ru/tekhnicheskaya-podderzhka/razrabotchikam-programmnogo-obespecheniya

### Настройка и управление сервисом
nano /etc/systemd/system/flex_receiver.service
``` bash
[Unit]
Description=flex_receiver
# Указывает, что юнит должен быть запущен после группы указанных сервисов
After=syslog.target
After=network.target
After=mysql.service
[Service]
Type=simple
PIDFile=/var/lib/flex_receiver.pid
WorkingDirectory=/projects/flex_receiver
User=root
Group=root
Environment=PYTHONPATH=/projects/flex_receiver
OOMScoreAdjust=-100
ExecStart=/usr/bin/python3 -u flex_receiver.py
#ExecStop=
#ExecReload=
TimeoutSec=300
Restart=always
[Install]
WantedBy=multi-user.target
```
``` bash
systemctl start flex_receiver
systemctl status flex_receiver
systemctl stop flex_receiver
journalctl -u flex_receiver.service -f -n 50
```

### Настройка архивации
* crontab -e
``` bash
  20 4 * * 1-7 mysqldump gnss|gzip -c|ssh 172.22.220.55 "cat >/backup/gnss/db_`date "+%Y-%m-%d_%H%M%S"`.gz"
```

### Настройка периодической отправки статуса
* crontab -e
``` bash
0 10,20 * * 1-7 cd /projects/flex_receiver && python3 scheduled_message.py >>/var/scheduled_message.log 2>>/var/scheduled_message.err
```

### Настройка геозон
* https://yandex.ru/dev/maps/jsbox/2.1/geoobject_events

### TODO Админка на Flask
* https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login-ru
* https://secondtruth.github.io/startmin/pages/flot.html
* https://github.com/secondtruth/startmin