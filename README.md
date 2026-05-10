# FastAPI Task API
## Tests
Install dependencies:
```bash
./venv/bin/pip install -r requirements.txt
```

Run all tests:

```bash
./venv/bin/python -m pytest tests
```

Run tests with coverage:

```bash
./venv/bin/python -m coverage run -m pytest tests
./venv/bin/python -m coverage report -m app/*.py app/routers/*.py
./venv/bin/python -m coverage html
```

Current application coverage: 82%.

The generated HTML coverage report is available at:

```txt
htmlcov/index.html
```

This file can be opened in a browser to view coverage details without running the code.

## Load Testing

Start the API:

```bash
./venv/bin/uvicorn app.main:app --reload
```

Run Locust with the web UI:

```bash
./venv/bin/locust -f locustfile.py -H http://127.0.0.1:8000
```

Then open:

```txt
http://localhost:8089
```

Run a short headless load test and generate an HTML report:

```bash
./venv/bin/locust -f locustfile.py -H http://127.0.0.1:8000 --headless -u 5 -r 2 -t 10s --html locust-report.html
```

The latest load-test HTML report is available at:

```txt
locust-report.html
```
