Предврительно необходимо добавить .env в директории запуска контейнеров:
ln -s ../../.env .env

--------------------------------------------------------------------------------------------------

Запуск контейнеров:
docker compose up
или
docker compose up -d (запускаются в фоновом режиме)

Проверить:
docker ps

```bash
develop git:(config-docker) ✗ docker ps
CONTAINER ID   IMAGE                COMMAND                  CREATED        STATUS        PORTS                                         NAMES
4ca38923bfd1   postgres:15-alpine   "docker-entrypoint.s…"   17 hours ago   Up 17 hours   0.0.0.0:5432->5432/tcp, [::]:5432->5432/tcp   dev-postgresql
f8612c61e2df   develop-dev-app      "bash"                   17 hours ago   Up 17 hours   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp   dev-app
```

Удалить контейнеры вместе с томами:
docker compose down -d

При создании контейнера с нуля бд сама инициализируется.

--------------------------------------------------------------------------------------------------

В докере приложения запускается bash. Чтобы запустить FastApi сервер используйте:
docker compose exec dev-app uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

Для запуска тестов
docker compose exec dev-app pytest test/
