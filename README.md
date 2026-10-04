# Специализированная база знаний (для сергея васильевича)

1. **Сборка/запуск compose**

```bash
    docker compose --project-name sbz -f compose.yml up -d --build
```

1. **Миграции базыданных**

После запуска контейнера необходимо приминить миграции

```bash
alembic upgrade head
```

