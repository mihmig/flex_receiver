DROP TABLE gnss.geo_zone;

CREATE TABLE gnss.geo_zone (
    id INT AUTO_INCREMENT COMMENT 'id записи в БД',
    parent_id INT COMMENT 'id родительской зоны',
    `name` VARCHAR(128) NOT NULL COMMENT 'Имя',
    `source` VARCHAR(128) NOT NULL COMMENT 'Источник',
    tags VARCHAR(256) NOT NULL COMMENT 'Теги',
    source_geo TEXT NOT NULL COMMENT 'Координаты вершин/точек/центра',
    radius FLOAT COMMENT 'Радиус окружности, м.',
    alert BOOL NOT NULL DEFAULT false COMMENT 'Уведомлять о входе-выходе в зону',
    enabled BOOL NOT NULL DEFAULT false COMMENT 'Разрешено использовать зону',
    type ENUM('CIRCLE','POLIGON','LINE') NOT NULL COMMENT 'Тип геозоны',
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Дата внесения в БД',
    updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Дата последнего изменнения',
    PRIMARY KEY (`id`)
);
ALTER TABLE gnss.geo_zone COMMENT='Геозоны';