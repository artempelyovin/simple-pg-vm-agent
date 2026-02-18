# simple-pg-vm-agent

Реализация простейшего PostgreSQL VM агента как части DBaaS сервиса (в учебных целях)

## Push VS Pull модель

В рамках архитектуры DBaaS-агента возможны две модели взаимодействия между **Control Plane** и **Agent (на VM)**.

**Push модель:**

```
 Control Plane --> Agent on VM
```

**Pull модели:**

```
 Control Plane <-- Agent on VM
```

В рамках данного учебного проекта используется **Push-модель**, поскольку:

- Проще в реализации;
- Удобна для локального тестирования (Control Plane - не реальный сервис, а просто CURL запросы к агенту);


## Roadmap

- [X] Установка Postgres (`docker pull` + `docker run`)
- [X] Остановка Postgres (`docker stop`)
- [X] Запуск Postgres (`docker start`)
- [ ] Проверка статуса (`docker ps` + healthcheck)
- [ ] SQLite Storage 
