-- DROP TABLE gnss.lbs;

CREATE TABLE gnss.lbs (
    id BIGINT COMMENT 'id',
    num INT COMMENT 'Номер',
    lat FLOAT COMMENT 'Широта',
    lon FLOAT COMMENT 'Долгота',
    locType INT COMMENT 'Непонятно',
    bsType INT COMMENT 'Непонятно',
    bands VARCHAR(255) COMMENT 'Диапазон(ы)',
    valid BOOL DEFAULT FALSE COMMENT 'Информация валидна',
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Дата внесения в БД',
    updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Дата последнего изменнения',
    PRIMARY KEY (`id`),
    INDEX idx_lbs_lat_lon (lat, lon),
    INDEX idx_lbs_valid (valid)
);
ALTER TABLE gnss.lbs COMMENT='Базовые станции';