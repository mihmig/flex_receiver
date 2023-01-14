## Приём телеметрии с GNSS-трекеров по протоколу FLEX

### Установка
pip install -r requirements.txt
MARIADB: 
mysqlimport --local --fields-terminated-by=";" --lines-terminated-by="\r\n" -d -v gnss event.csv
mysqlimport --local --fields-terminated-by=";" --lines-terminated-by="\r\n" -d -v gnss parameter.csv