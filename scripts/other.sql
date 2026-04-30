

-- SQL‑запрос для подсчёта количества записей в таблице message за указанный период с группировкой по часам:
-- docker logs --since "2026-04-26T05:00:00" --until "2026-04-26T09:00:00" flex
SELECT
    DATE_FORMAT(`datetime`, '%Y-%m-%d %H:00:00') AS hour_interval,
    COUNT(*) AS message_count
FROM `message`
WHERE device_id = 8
  AND `datetime` >= '2026-04-26 05:00:00'
  AND `datetime` < '2026-04-26 10:00:00'
GROUP BY DATE_FORMAT(`datetime`, '%Y-%m-%d %H')
ORDER BY hour_interval;


-- Очищаем таблицу от записей ботов (как они туда попадают?)
DELETE FROM message WHERE device_id=6;
-- Очищаем таблицу message от записей старше 2-х недель
DELETE FROM message WHERE device_id=8 AND datetime < NOW() - INTERVAL 14 DAY;

-- Список пользователей БД
SELECT User, Host, Password FROM mysql.user;

-- Автоочистка таблицы message от записей старше 2-х недель
CREATE EVENT IF NOT EXISTS daily_delete_old_rows
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_TIMESTAMP
DO
  DELETE FROM message WHERE device_id=8 AND datetime < NOW() - INTERVAL 14 DAY;

SHOW EVENTS;


SHOW CREATE EVENT daily_delete_old_rows;

ALTER EVENT daily_delete_old_rows DISABLE;
ALTER EVENT daily_delete_old_rows ENABLE;
DROP EVENT IF EXISTS daily_delete_old_rows;


-- Добавляем столбцы в таблицу device
ALTER TABLE device ADD COLUMN `debug` bool NOT NULL default FALSE COMMENT 'Флаг отладки сообщений от устройства';
ALTER TABLE device ADD COLUMN `alert` bool NOT NULL default FALSE COMMENT 'Флаг отправки сообщений по устройству';
ALTER TABLE device ADD COLUMN `telegram_chat_id` BIGINT COMMENT 'ID телеграм-чата, в который отправлять сообщения';
ALTER TABLE device ADD COLUMN `max_chat_id` BIGINT COMMENT 'ID МАКС-чата, в который отправлять сообщения';

ALTER TABLE monitoring ADD COLUMN `telegram_chat_id` BIGINT COMMENT 'ID телеграм-чата, в который отправлять сообщения';
ALTER TABLE monitoring ADD COLUMN `max_chat_id` BIGINT COMMENT 'ID МАКС-чата, в который отправлять сообщения';
UPDATE monitoring SET telegram_chat_id=chat_id;
UPDATE monitoring SET alert = true;


-- Матиз - Онлайн
UPDATE device SET device.last_alive = now() WHERE device.imei='862531045630978';
-- Матиз - Офлайн
UPDATE device SET device.last_alive = DATE_SUB(now(), INTERVAL 1 DAY) WHERE device.imei='862531045630978';

-- Матиз - датчики - ОНЛАЙН
UPDATE monitoring SET `datetime` = now() WHERE device_id = 1;
-- Матиз - датчики - ОФЛАЙН
UPDATE monitoring SET `datetime` = DATE_SUB(now(), INTERVAL 2 HOUR ) WHERE device_id = 1;
