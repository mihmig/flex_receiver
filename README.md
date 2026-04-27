## Приём телеметрии с GNSS-трекеров по протоколу FLEX

### Установка
* Установка зависимостей (библиотек python)
  python3 -m pip install --upgrade pip
  pip install -r requirements.txt
* Загрузка справочников:
* MariaDB (MySql):
    ``` bash
    mysql
    usq mysql
    select host, user, password from user;
    mysqlimport --local --fields-terminated-by=";" --lines-terminated-by="\r\n" -d -v gnss event.csv
    mysqlimport --local --fields-terminated-by=";" --lines-terminated-by="\r\n" -d -v gnss parameter.csv
    ```
### Запуск для отладки локально
PYTHONUNBUFFERED=1;DATABASE_HOST=localhost;DATABASE_PORT=8003;DATABASE_NAME=gnss;DATABASE_USER=gnss;DATABASE_PASSWORD=gnss
### Установка в докере

* git clone git@github.com:mihmig/flex_receiver.git cd /opt/flex_receiver
* cd /opt/flex_receiver
* docker-compose up flex-db
* docker exec flex-db /bin/bash -c 'mariadb gnss -p$MYSQL_ROOT_PASSWORD </backup/gnss.sql'
* docker-compose up flex --build
* 
### При запуске на Centos/Almalinux нужно открыть порт firewall-а
firewall-cmd --permanent --add-port=21626/udp

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
systemctl daemon-reload
systemctl start flex_receiver
systemctl status flex_receiver
systemctl stop flex_receiver
journalctl -u flex_receiver.service -f -n 50

PYTHONPATH=/projects/flex_receiver/ /usr/local/bin/python3.10 test/test_telegram.py
PYTHONPATH=/projects/flex_receiver/ /usr/local/bin/python3.10 test/test_telegram.py
```

### Настройка архивации
* crontab -e
``` bash
  20 4 * * 1-7 mysqldump gnss|gzip -c|ssh 172.22.220.55 "cat >/backup/gnss/db_`date "+%Y-%m-%d_%H%M%S"`.gz"
```

### Запуск в докере
docker-compose up -d --build flex

### Архивация 
* docker exec flex-db /bin/bash -c 'mariadb-dump gnss -p$MYSQL_ROOT_PASSWORD >/backup/gnss.sql'

### Восстановление
* docker exec flex-db /bin/bash -c 'mariadb gnss -p$MYSQL_ROOT_PASSWORD </backup/gnss.sql'
* Для windows 
  * docker exec flex-db /bin/bash -c "mariadb gnss -p$MYSQL_ROOT_PASSWORD </backup/gnss.sql"

### Настройка периодической отправки статуса
* crontab -e
``` bash
0 10,20 * * 1-7 cd /projects/flex_receiver && python3 scheduled_message.py >>/var/scheduled_message.log 2>>/var/scheduled_message.err
```

#### Удаление ненужных исторических данных
* [LINUX] docker exec flex-db /bin/bash -c 'mariadb gnss -p$MYSQL_ROOT_PASSWORD -e "DELETE FROM message WHERE device_id=8 AND datetime < DATE_SUB(NOW(), INTERVAL 2 WEEK);"' 
* [WINDOWS] docker exec flex-db /bin/bash -c "mariadb gnss -p$MYSQL_ROOT_PASSWORD -e 'DELETE FROM message WHERE device_id=8 AND datetime < DATE_SUB(NOW(), INTERVAL 2 WEEK);'" 
* DELETE FROM message WHERE device_id = 1 AND message_type IN ('h','a');
* DELETE FROM message WHERE device_id = 6
* 
``` sql 
CREATE EVENT IF NOT EXISTS daily_delete_old_rows
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_TIMESTAMP
DO
  DELETE FROM message WHERE device_id=8 AND datetime < NOW() - INTERVAL 14 DAY;
```  
* [1105] Event scheduler is switched off, use SET GLOBAL event_scheduler=ON to enable it.
* 

### Настройка геозон
* https://yandex.ru/dev/maps/jsbox/2.1/geoobject_events

### TODO Админка на Flask
* https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login-ru
* https://secondtruth.github.io/startmin/pages/flot.html
* https://github.com/secondtruth/startmin

### Алгоритм уведомлений, когда параметр "колеблется" около границы нормы: 
1. Проверить уведомления о выходе из нормы и возврату к норме показателей.
2. Внепланово уведомлять об этом
3. Проверить уведомления о долгом отсутствии связи. Предлагаю сделать критичным интервал 4 часа и вернуть уведомления об этом
4. Нужно после восстановления связи п.3 передавать внеплановое стандартное сообщение о текущем состоянии параметров 


1. Если параметр вышел за пределы и прошло более 30 минут
2. И время, когда параметр был в норме больше 30 минут 
То:
1. Ставим статус "alert!"
2. Уведомляем


1. Если параметр "вошёл" в норму:
2. Текущий статус "alert!"
3. Время, когда он был "не в норме" - более 30 минут
То:
1. Снимаем статус "alert"
2. Уведомляем о возврате параметра в норму

### Запуск локально
PYTHONUNBUFFERED=1;DATABASE_HOST=localhost;DATABASE_PORT=8003;DATABASE_NAME=gnss;DATABASE_USER=gnss;DATABASE_PASSWORD=gnss


### Обслуживание



### Передаваемые параметры

* 10 Последняя валидная широта Угол широты, зафиксированный при получении последних валидных координат. В десятитысячных долях минуты.
* Например, 55° 42,2389' будет представлено как 33422389
* 11 Угол долготы, зафиксированный при получении последних валидных координат. В десятитысячных долях минуты.
* Например, 37° 41,6063' будет представлено как 22616063
* 12 Высота относительно уровня моря, зафиксированная при получении последних валидных координат: В дециметрах Например, 205 метров будет представлено как 2050 дециметров
* 13 Скорость, зафиксированная при получении последних валидных координат. В км/ч
* 14 Курс, зафиксированный при получении последних валидных координат.