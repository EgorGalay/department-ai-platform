# Department AI Platform

Локальная AI-платформа кафедры. На первом этапе подготовлен каркас backend и стартовая web-страница; база данных, авторизация и AI-функции будут добавляться отдельными этапами.

## Требования для локального запуска

- Python 3.12 и [uv](https://docs.astral.sh/uv/).
- Node.js 20.9 или новее и npm для frontend.

## Backend

В PowerShell из корня репозитория подготовь конфигурацию и запусти PostgreSQL:

```powershell
Copy-Item backend/.env.example backend/.env
docker compose up -d database
Set-Location backend
uv sync --dev
uv run alembic upgrade head
uv run python -m department_ai.modules.identity.bootstrap_admin
uv run uvicorn department_ai.main:app --reload
```

API: `http://localhost:8000/api/v1/health`. Проверка готовности БД: `http://localhost:8000/api/v1/ready`. Документация FastAPI: `http://localhost:8000/docs`.

Команда `bootstrap_admin` интерактивно создаёт первого администратора и не передаёт пароль через shell. Открытой регистрации нет. В разработке используется локальный ключ по умолчанию; для production задайте `ENVIRONMENT=production` и сгенерируйте `JWT_SECRET_KEY` командой `python -c "import secrets; print(secrets.token_hex(32))"`.

`development-only` в примерах конфигурации предназначен только для локального запуска. Для сервера нужно задать собственные секреты через окружение.

## Frontend

В отдельном терминале из корня репозитория:

```powershell
Set-Location frontend
npm install
npm run dev
```

Frontend: `http://localhost:3000`. Кнопка на стартовой странице открывает health endpoint backend.

## Структура

- `backend/src/department_ai/` — приложение FastAPI и модули.
- `backend/migrations/` и `backend/tests/` — миграции и проверки backend.
- `frontend/` — web-клиент Next.js.
- `infrastructure/`, `docker-compose.yml` — локальная инфраструктура (будет заполняться по мере добавления сервисов).
- `docs/` — архитектура и план разработки.
