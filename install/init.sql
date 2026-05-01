CREATE DATABASE gnss DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci;
CREATE USER 'gnss'@'%' IDENTIFIED BY 'gnss';
GRANT ALL PRIVILEGES ON gnss.* TO 'gnss'@'%';
FLUSH PRIVILEGES;

USE gnss;

-- DROP TABLE `device`
CREATE TABLE gnss.`device`
(
	id INT AUTO_INCREMENT COMMENT 'id устройства в БД',
	imei VARCHAR(255) NOT NULL COMMENT 'IMEI модема устройства',
	`name` VARCHAR(255) NULL COMMENT 'Название устройства',
	`comment` VARCHAR(255) NULL COMMENT 'Комментарий',
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Дата внесения в БД',
    last_alive TIMESTAMP COMMENT 'Дата получения последнего сообщения от устройства',
	CONSTRAINT device_pk PRIMARY KEY (id),
    UNIQUE (imei)
) ENGINE=InnoDB;

ALTER TABLE gnss.`device` COMMENT='Устройства';

DROP TABLE IF EXISTS settings;

CREATE TABLE gnss.`settings`
(
	`key` VARCHAR(255) NOT NULL COMMENT 'Код настройки',
	`value` VARCHAR(255) NULL COMMENT 'Название устройства',
	`comment` VARCHAR(255) NULL COMMENT 'Комментарий',
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Дата внесения в БД',
	CONSTRAINT settings_pk PRIMARY KEY (`key`)
) ENGINE=InnoDB;

ALTER TABLE gnss.`settings` COMMENT='Системные настройки';

INSERT INTO gnss.`settings` (`key`, value, comment) VALUES
('alert','0', 'Глобальный флаготправки уведомлений'),
('telegram_bot_token', '5699840798:AAGVDoe2qsZEpRbzO_YErjIyPsVY6EfBTFg', 'Токен Телеграм-бота'),
('telegram_chat_id', '-1001882219961', 'Id телеграм-чата для отправки уведомлений'),
('device_default_timeout', '3600', 'Интервал отсутствия связи с устройством по умолчанию'),
('sensor_default_timeout', '86400', 'Интервал отсутствия показания датчика по умолчанию'),
('fields_to_show', '1,2,3,19,49,51', 'Список полей, отображаемых в отладочных сообщениях'),
('max_bot_token', 'f9LHodD0cOKqTxdNESaAjKoLcE22Rdf06YZJIPIx9nzMoLymaLzP5oXdD-O51mplTs_ZsNTBSC65kef98WOA', 'Токет MAX-бота'),
('max_chat_id', '-71011425140800', 'Id MAX-чата для отправки уведомлений')


-- DROP TABLE gnss.`event`
CREATE TABLE gnss.`event`
(
    id INT NOT NULL COMMENT 'id события (см. справочник)',
    code VARCHAR(255) NOT NULL COMMENT 'Код события',
    description VARCHAR(512) NOT NULL COMMENT 'Описание события',
    PRIMARY KEY (`id`),
    UNIQUE (code)
) ENGINE=InnoDB;
ALTER TABLE gnss.`event` COMMENT='Коды и описания событий NTCB';


DROP TABLE gnss.`message`;
CREATE TABLE gnss.`message`
(
    id INT AUTO_INCREMENT COMMENT 'id записи в БД',
    device_id INT NOT NULL COMMENT 'id устройства',
    event_id INT COMMENT 'id события',
    `datetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Дата и время события',
    message_type CHAR(1) NOT NULL COMMENT 'Тип сообщения',
    -- Размер пакета не превышает 1,3 Кб (не считая заголовка)
    `data` BLOB NOT NULL COMMENT 'Двоичные данные сообщения',
    `decoded` LONGTEXT COMMENT 'Декодированное в JSON сообщение',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB;
ALTER TABLE gnss.`message` COMMENT='Журнал входящих сообщений';
CREATE INDEX `message__datetime_idx` ON gnss.`message` (`datetime` DESC);

DROP TABLE gnss.`parameter`;
CREATE TABLE gnss.`parameter`
(
    id INT COMMENT 'id параметра',
    `description` VARCHAR(1024) NOT NULL COMMENT 'Описание параметра',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB;
ALTER TABLE gnss.`parameter` COMMENT='Параметры мониторинга';

-- DROP TABLE gnss.`monitoring`
-- Указывается либо номер параметра (например температура цифрового датчика 1)
-- тогда контролируется выход значения за его пределы (или обрыв датчика)
-- либо код события (например 4884;T1_BREAK;Внешний температурный датчик №1 оборван)
DROP TABLE gnss.`monitoring`;
CREATE TABLE gnss.`monitoring`
(
    id INT AUTO_INCREMENT COMMENT 'id записи в БД',
    device_id INT NOT NULL COMMENT 'id устройства',
    parameter_id INT COMMENT 'Номер параметра',
    event_id INT COMMENT 'id события',
    `datetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Дата и время последнего события',
    current_value DECIMAL(15,3) COMMENT 'Текущее(последнее полученное) значение параметра',
    min_value DECIMAL(15,3) COMMENT 'Минимально допустимое значение параметра',
    max_value DECIMAL(15,3) COMMENT 'Максимально допустимое значение параметра',
    below_min_message VARCHAR(1024) COMMENT 'Сообщение при выходе параметра за нижний предел',
    above_max_message VARCHAR(1024) COMMENT 'Сообщение при выходе параметра за верхний предел',
    in_range_message VARCHAR(1024) COMMENT 'Сообщение при возвращении параметра в указанные пределы',
    no_data_message VARCHAR(1024) COMMENT 'Сообщение при неполучении параметра в течение определённого времени',
    data_resumption_message VARCHAR(1024) COMMENT 'Сообщение при возобновлении приёма параметра',
    event_message VARCHAR(1024) COMMENT 'Сообщение при наступлении события',
    timeout INT COMMENT 'Таймаут не предоставления данных, сек.',
    alert bool NOT NULL DEFAULT FALSE COMMENT 'Уведомлять о наступлении события?',
    triggered bool NOT NULL DEFAULT FALSE COMMENT 'Признак сработки условия выхода значения параметра за границы',
    triggered_timeout bool NOT NULL DEFAULT FALSE COMMENT 'Признак сработки условия недоступности датчика',
    chat_id BIGINT COMMENT 'id телеграм-чата для отправки сообщений',
    PRIMARY KEY (`id`),
    UNIQUE (device_id, parameter_id)
) ENGINE=InnoDB;
ALTER TABLE gnss.`monitoring` COMMENT='Параметры и коды событий, которые нужно мониторить';
CREATE INDEX `monitoring__device_id_idx` ON gnss.`monitoring` (device_id);

INSERT INTO gnss.monitoring (id, device_id, parameter_id, event_id, datetime, current_value, min_value, max_value, below_min_message, above_max_message, no_data_message, event_message, alert, triggered)
VALUES (1, 1, 45, null, '2023-01-11 23:17:04', null, -10.000, -5.000, 'Температура на улице меньше заданного значения', 'Температура на улице больше заданного значения', 'Нет данных о температуре', null, 1, 0);

DROP TABLE gnss.geo_zone;
-- https://mariadb.com/kb/en/geometry-types/
CREATE TABLE gnss.geo_zone (
    id INT AUTO_INCREMENT COMMENT 'id записи в БД',
    parent_id INT COMMENT 'id родительской зоны',
    `name` VARCHAR(128) NOT NULL COMMENT 'Имя',
    `source` VARCHAR(128) NOT NULL COMMENT 'Источник',
    tags VARCHAR(256) NOT NULL COMMENT 'Теги',
    source_geo TEXT NOT NULL COMMENT 'Координаты вершин/точек/центра',
    alert BOOL NOT NULL DEFAULT false COMMENT 'Уведомлять о входе-выходе в зону',
    enabled BOOL NOT NULL DEFAULT false COMMENT 'Разрешено использовать зону',
    type ENUM('CIRCLE','POLIGON','LINE') NOT NULL COMMENT 'Тип геозоны',
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Дата внесения в БД',
    updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Дата последнего изменнения',
    PRIMARY KEY (`id`)
);
ALTER TABLE gnss.geo_zone COMMENT='Геозоны';

ALTER TABLE gnss.monitoring ADD COLUMN with_device BOOL DEFAULT FALSE COMMENT 'Добавлять имя устройства в сообщениях';
ALTER TABLE gnss.message ADD COLUMN moment TIMESTAMP NOT NULL
    COMMENT 'Дата и время регистрации события';

ALTER TABLE gnss.message ADD COLUMN received TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    COMMENT 'Дата и время получения события';
-- Круг радиусом 10 км от центра Ярославля
# INSERT INTO gnss.geo_zone (type, center, radius) VALUES ('CIRCLE',
#                                                          PointFromText('POINT(39.90991271972598 57.62478929076413)'),
#                                                          10000);
#
# SELECT ST_AsText(center), ST_X(center), ST_Y(center) FROM gnss.geo_zone WHERE id = 2;
# ,
#     center POINT COMMENT 'Центр круга',
#     radius INT COMMENT 'Радиус круга, м.',
#     `poligon` POLYGON COMMENT 'Точки полигона',
#     `line` MULTIPOINT COMMENT 'Точки трека',