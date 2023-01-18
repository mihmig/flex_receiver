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
