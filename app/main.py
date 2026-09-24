from fastapi import FastAPI

app = FastAPI(title="AI200 API", version="0.1.0")


@app.get("/")
def read_root():
    return {"message": "Hello from the AI200 API"}


@app.get("/health")
def health_check():
    return {"status": "ok done"}
