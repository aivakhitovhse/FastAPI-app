# FastAPI Task API
## Tests
Установка dependencies:
```bash
./venv/bin/pip install -r requirements.txt
```

Запись всех тестов:
```bash
./venv/bin/python -m pytest tests
```

Запух всех тестов:
```bash
./venv/bin/python -m coverage run -m pytest tests
./venv/bin/python -m coverage report -m app/*.py app/routers/*.py
./venv/bin/python -m coverage html
```

Тестовое покрытие: 82%.

 HTML:

```txt
htmlcov/index.html
```

Можно посмотреть.

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
 Запустить HTML репопт:

```bash
./venv/bin/locust -f locustfile.py -H http://127.0.0.1:8000 --headless -u 5 -r 2 -t 10s --html locust-report.html
```

Последний HTML репорт:

```txt
locust-report.html
```
