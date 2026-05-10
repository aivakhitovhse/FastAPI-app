# FastAPI Task API
## Tests
Установка dependencies:
```bash
./venv/bin/pip install -r requirements.txt
```

Запуск всех тестов:
```bash
./venv/bin/python -m pytest tests
```

Запуск тестов с проверкой покрытия:
```bash
./venv/bin/python -m coverage run -m pytest tests
./venv/bin/python -m coverage report -m app/*.py app/routers/*.py
./venv/bin/python -m coverage html
```

Тестовое покрытие приложения: 95%.

HTML-отчет покрытия:

```txt
htmlcov/index.html
```

Файл можно открыть в браузере без запуска кода.

## Load Testing

Запуск API:

```bash
./venv/bin/uvicorn app.main:app --reload
```

Запуск Locust:

```bash
./venv/bin/locust -f locustfile.py -H http://127.0.0.1:8000
```

Посмотреть:

```txt
http://localhost:8089
```
Запустить Locust и создать HTML-репорт:

```bash
./venv/bin/locust -f locustfile.py -H http://127.0.0.1:8000 --headless -u 5 -r 2 -t 10s --html locust-report.html
```

Последний HTML-репорт:

```txt
locust-report.html
```
