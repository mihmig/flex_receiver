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