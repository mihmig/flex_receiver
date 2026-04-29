#!/usr/bin/env bash
docker exec flex-db /bin/bash -c 'mariadb-dump gnss -p$MYSQL_ROOT_PASSWORD >/backup/gnss.sql'