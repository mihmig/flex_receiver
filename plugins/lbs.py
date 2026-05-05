# Модуль получения данных о вышках сотовой связи

# План такой:
# Указываем центральную точку ссылкой:
# https://yandex.com/maps/16/yaroslavl/?ll=39.891362%2C57.621132&z=14.98
#
# curl 'https://4cells.ru:4444/api/map/enb/lte/250099?latStart=57.62566431450651&latEnd=57.76584103467539&lonStart=39.69385581481414&lonEnd=39.835198692630485' \
#   -H 'accept: application/json, text/plain, */*' \
#   -H 'accept-language: ru-RU,ru;q=0.5' \
#   -H 'origin: https://4cells.ru' \
#   -H 'priority: u=1, i' \
#   -H 'referer: https://4cells.ru/' \
#   -H 'sec-ch-ua: "Brave";v="147", "Not.A/Brand";v="8", "Chromium";v="147"' \
#   -H 'sec-ch-ua-mobile: ?0' \
#   -H 'sec-ch-ua-platform: "Windows"' \
#   -H 'sec-fetch-dest: empty' \
#   -H 'sec-fetch-mode: cors' \
#   -H 'sec-fetch-site: same-site' \
#   -H 'sec-gpc: 1' \
#   -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36' \
#   -H 'x-request-id: 3363909ce29c184c8807a3502bf3094cbd58779283c1180d1d1d91c9832cb876'

