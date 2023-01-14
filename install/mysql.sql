CREATE DATABASE gnss DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci;
CREATE USER 'gnss'@'%' IDENTIFIED BY 'gnss';
GRANT ALL PRIVILEGES ON gnss.* TO 'gnss'@'%';
FLUSH PRIVILEGES;

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
    no_data_message VARCHAR(1024) COMMENT 'Сообщение при неполучении данных',
    event_message VARCHAR(1024) COMMENT 'Сообщение при наступлении события',
    timeout INT COMMENT 'Таймаут не предоставления данных, сек.',
    alert bool NOT NULL DEFAULT FALSE COMMENT 'Уведомлять о наступлении события?',
    triggered bool NOT NULL DEFAULT FALSE COMMENT 'Признак сработки условия',
    PRIMARY KEY (`id`),
    UNIQUE (device_id, parameter_id)
) ENGINE=InnoDB;
ALTER TABLE gnss.`monitoring` COMMENT='Параметры и коды событий, которые нужно мониторить';
CREATE INDEX `monitoring__device_id_idx` ON gnss.`monitoring` (device_id);

INSERT INTO gnss.monitoring (id, device_id, parameter_id, event_id, datetime, current_value, min_value, max_value, below_min_message, above_max_message, no_data_message, event_message, alert, triggered) VALUES (1, 1, 45, null, '2023-01-11 23:17:04', null, -10.000, -5.000, 'Температура на улице меньше заданного значения', 'Температура на улице больше заданного значения', 'Нет данных о температуре', null, 1, 0);
