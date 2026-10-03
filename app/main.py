from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="AI200 API ", version="0.1.0")


@app.get("/", response_class=HTMLResponse)
def read_root():
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>{app.title}</title>
        <style>
            body {{
                font-family: system-ui, sans-serif;
                display: flex;
                justify-content: center;
                min-height: 100vh;
                margin: 0;
                padding-top: 4rem;
                background: #0f172a;
                color: #e2e8f0;
            }}
            .card {{
                background: #1e293b;
                padding: 2.5rem 3rem;
                border-radius: 12px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
                text-align: center;
                height: fit-content;
            }}
            h1 {{
                margin: 0 0 1rem;
                font-size: 1.75rem;
            }}
            .status {{
                display: inline-block;
                padding: 0.25rem 0.75rem;
                border-radius: 999px;
                background: #166534;
                color: #bbf7d0;
                font-weight: 600;
                font-size: 0.85rem;
            }}
            .version {{
                margin-top: 1rem;
                color: #94a3b8;
                font-size: 0.9rem;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>{app.title}</h1>
            <span class="status">Server Running</span>
            <div class="version">Version- {app.version}</div>
        </div>
    </body>
    </html>
    """


@app.get("/health")
def health_check():
    return {"status": "ok done"}
