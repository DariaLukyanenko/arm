#!/bin/bash

set -e

GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}Ожидание БД${NC}"
until pg_isready -h /var/run/postgresql -U postgres; do
    echo "..."
    sleep 1
done

echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] - Инициализация БД${NC}"
${POSTGRES_SOURCE}/db_helper.sh postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@/${POSTGRES_DB}?host=/var/run/postgresql -b
