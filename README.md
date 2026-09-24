# AI200 API

A small FastAPI service, containerised and served on port 8080.

## Run with Docker

```bash
docker build -t ai200-api .
docker run --rm -p 8080:8080 ai200-api
```

Then open:

- http://localhost:8080/ - hello message
- http://localhost:8080/health - health check
- http://localhost:8080/docs - interactive API docs

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```
