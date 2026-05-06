-- DROP TABLE gnss.lbs;

CREATE TABLE gnss.lbs (
    id BIGINT COMMENT 'id',
    num INT NOT NULL COMMENT 'Номер',
    lat FLOAT NOT NULL COMMENT 'Широта',
    lon FLOAT NOT NULL COMMENT 'Долгота',
    locType INT NOT NULL COMMENT 'Непонятно',
    bsType INT NOT NULL COMMENT 'Непонятно',
    bands VARCHAR(255) NOT NULL COMMENT 'Диапазон(ы)',
    valid BOOL NOT NULL DEFAULT FALSE COMMENT 'Информация валидна',
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Дата внесения в БД',
    updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Дата последнего изменнения',
    PRIMARY KEY (`id`),
    INDEX idx_lbs_lat_lon (lat, lon),
    INDEX idx_lbs_valid (valid)
);
ALTER TABLE gnss.lbs COMMENT='Базовые станции';