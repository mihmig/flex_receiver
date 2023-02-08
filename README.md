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

### Документация
* https://www.navtelecom.ru/ru/tekhnicheskaya-podderzhka/razrabotchikam-programmnogo-obespecheniya

### Настройка архивации
* crontab -e
``` bash
  20 4 * * 1-7 mysqldump gnss|gzip -c|ssh 172.22.220.55 "cat >/backup/gnss/db_`date "+%Y-%m-%d_%H%M%S"`.gz"
```
### Настройка геозон
* https://yandex.ru/dev/maps/jsbox/2.1/geoobject_events

### TODO Админка на Flask
* https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login-ru
* https://secondtruth.github.io/startmin/pages/flot.html
* https://github.com/secondtruth/startmin