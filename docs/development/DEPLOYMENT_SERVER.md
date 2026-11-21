# Запуск на Linux-сервере в локальной сети

## Требования

- Git и Docker Compose v2 на сервере.
- Ollama запущена на сервере и отвечает на `127.0.0.1:11434`.
- У пользователя есть `sudo` для Docker, доступ к репозиторию и возможность открыть порты 3000 и 8000 в локальной сети.

## Подготовка

На сервере клонируй репозиторий или обнови существующую копию:

```bash
git clone https://github.com/EgorGalay/department-ai-platform.git
cd department-ai-platform
```

Создай файлы локальной конфигурации. Не копируй `.env` с компьютера разработчика:

```bash
cp infrastructure/compose/server.env.example infrastructure/compose/server.env
cp backend/.env.example backend/.env
openssl rand -hex 24
openssl rand -hex 32
```

В `infrastructure/compose/server.env` помести первый случайный результат в `POSTGRES_PASSWORD`. Проверь `SERVER_HOST` и `PUBLIC_FRONTEND_ORIGIN` по адресу сервера.

В `backend/.env` помести второй результат в `JWT_SECRET_KEY` и установи `ENVIRONMENT=production`. Остальные локальные секреты на сервер не копируй. Compose задаст адрес PostgreSQL и Ollama для сервера.

## Запуск

Из корня репозитория:

```bash
sudo docker compose --env-file infrastructure/compose/server.env -f infrastructure/compose/docker-compose.server.yml up -d --build
sudo docker compose --env-file infrastructure/compose/server.env -f infrastructure/compose/docker-compose.server.yml ps
```

Миграции применяются при старте backend. Для первого администратора выполни bootstrap внутри контейнера:

```bash
sudo docker compose --env-file infrastructure/compose/server.env -f infrastructure/compose/docker-compose.server.yml exec backend python -m department_ai.modules.identity.bootstrap_admin
```

Открой `http://SERVER_HOST:3000`. Swagger доступен по `http://SERVER_HOST:8000/docs`. SSH-туннель модели не нужен: backend контейнер использует Ollama на loopback сервера.

Для обновления после `git pull` повтори `docker compose ... up -d --build`. База сохраняется в volume `server_postgres_data`.
