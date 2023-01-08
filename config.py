config = {
    'telegram': {
        'bot_token': '5817521719:AAGuzDyzjnR2HXvtdhTh4gRr1LV15AjvdZ8',
        # Основной чат (для уведомлений)
        'chat_id': '-773583799',
        # Служебный чат (для сообщений об ошибках и т.п.)
        'service_chat_id': '47254369'
    },
    # Список полей, отображаемых в отладочных сообщениях
    'fields_to_show' : ['1', '2', '3', '19', '20', '45'],
    'storage': 'db_mysql',
    'database': {
        'dbname': 'gps',
        'user': 'gps',
        'password': 'gps',
        'host': 'mysql.lan',
        'port': 3306
    }
}
