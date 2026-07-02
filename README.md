<div align="center">
<a href="https://gradio.app">
<img src="readme_files/gradio.svg" alt="gradio" width=350>
</a>
</div>

<div align="center">

![Python version](https://img.shields.io/badge/python-3.10+-important)
![License](https://img.shields.io/badge/license-Apache%202.0-blue)

[GitHub](https://github.com/BF667/gradio-server)

</div>

# Gradio Server: Use Gradio as a Backend API Engine

A fork of [Gradio](https://github.com/gradio-app/gradio) enhanced with **custom frontend support** — use Gradio purely as a backend API server while serving your own web app (React, Vue, Svelte, plain HTML, or any static site) at the root URL.

No Gradio UI is rendered. You get Gradio's powerful queue, SSE streaming, file upload/download, and concurrency control — all callable from your own frontend via `/gradio_api/*`.

---

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/BF667/gradio-server.git
cd gradio-server

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install in editable mode (installs all dependencies automatically)
pip install -e .

# 4. Run a demo
python demo/custom_frontend_static/run.py
```

Open **http://localhost:7860** — you'll see your custom frontend, not the Gradio UI.

> **No PyPI install needed.** Everything runs from the cloned repo. `pip install -e .` just installs the dependencies listed in `requirements.txt` and links the local `gradio/` package.

---

## Two Ways to Use Gradio as a Backend

### 1. `gr.Blocks` + `gr.api()` — Minimal API Server

Register Python functions as API endpoints using `gr.api()`. They derive input/output types from type hints — no Gradio UI components needed.

```python
import gradio as gr

def reverse(text: str) -> str:
    return text[::-1]

def echo(message: str) -> str:
    return f"Echo: {message}"

with gr.Blocks() as demo:
    gr.api(reverse, api_name="reverse")
    gr.api(echo, api_name="echo")

demo.launch(custom_frontend="./my-website/")
```

This serves your static files from `./my-website/` at `/`, while the Gradio API is available at `/gradio_api/call/reverse` and `/gradio_api/call/echo`.

### 2. `Server()` — Full Backend with Custom REST + Gradio API

`Server` inherits from FastAPI, giving you full control over routes while also supporting Gradio-powered API endpoints.

```python
from gradio import Server
from fastapi import HTTPException
from pydantic import BaseModel

server = Server(title="My App", docs_url="/docs")

# Standard FastAPI routes — your own REST API
@server.get("/api/tasks")
def list_tasks():
    return [{"id": 1, "title": "Learn Gradio", "done": False}]

# Gradio-powered endpoint — queue + SSE streaming built in
@server.api(name="chat")
def ai_chat(message: str) -> str:
    return f"You said: {message}"

server.launch(
    custom_frontend="./frontend-dist/",
    spa=True,  # Enable client-side routing (React Router, Vue Router, etc.)
)
```

Three things coexist in one server:
- **Custom REST routes** (`/api/tasks`) — standard FastAPI
- **Gradio API endpoints** (`/gradio_api/call/chat`) — queue + SSE streaming
- **Your static frontend** served at `/`

---

## Key Parameters

### `custom_frontend` (str | Path | None)

Path to a directory containing your web app (index.html, JS bundles, CSS, images, etc.). When set, these files are served at `/` instead of the default Gradio UI.

All Gradio API endpoints under `/gradio_api/*` remain fully operational.

### `spa` (bool, default `False`)

When `True` (must be used with `custom_frontend`), any path that doesn't match a real file falls back to serving `index.html`. This enables client-side routers like React Router, Vue Router, SvelteKit, or hash-based routing to work seamlessly.

### `_frontend` (bool, default `True`)

Set to `False` to prevent Gradio from opening a browser tab on launch. Recommended for server/headless usage.

---

## What Stays Available with a Custom Frontend

Even when Gradio's own UI is replaced, everything else keeps working:

| Feature | Endpoint / Mechanism |
|---|---|
| API calls (queue + SSE) | `POST /gradio_api/call/<name>` → `GET /gradio_api/call/<name>/<event_id>` |
| API info | `GET /gradio_api/` |
| App config | `GET /gradio_api/config/` |
| File upload | Via Gradio queue (multipart) |
| File download | Via Gradio queue |
| Custom FastAPI routes | Whatever you defined on the `Server` |
| OpenAPI docs | `GET /docs` (if `docs_url` is set) |
| Health check | `GET /` (serves your `index.html`) |

---

## Calling the Gradio API from Your Frontend

Gradio uses a two-step SSE (Server-Sent Events) pattern:

```javascript
async function callGradio(apiName, data) {
    // Step 1: POST to queue — returns an event_id
    const res = await fetch(`/gradio_api/call/${apiName}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ data }),
    });
    const { event_id } = await res.json();

    // Step 2: Connect EventSource to stream the result
    return new Promise((resolve) => {
        const es = new EventSource(`/gradio_api/call/${apiName}/${event_id}`);
        es.onmessage = (e) => {
            const msg = JSON.parse(e.data);
            if (msg.msg === "process_completed") {
                es.close();
                resolve(msg.output.data);
            }
        };
    });
}

// Usage:
const result = await callGradio("reverse", ["hello world"]);
console.log(result); // ["dlrow olleh"]
```

---

## Demo Examples

### Static HTML Frontend (`demo/custom_frontend_static/`)

A plain HTML/CSS/JS site that calls two Gradio API endpoints (`reverse`, `echo`). No framework, no build step — just files.

```bash
pip install -e .
python demo/custom_frontend_static/run.py
```

**What it shows:**
- `gr.Blocks()` with `gr.api()` — API-only, zero UI components
- Static files served directly from the demo directory
- Dark-themed UI with "Reverse Text" and "Echo Message" cards

### Fullstack SPA (`demo/custom_frontend_fullstack/`)

A single-page app with hash-based routing that calls BOTH custom FastAPI routes AND Gradio API endpoints.

```bash
pip install -e .
python demo/custom_frontend_fullstack/run.py
```

**What it shows:**
- `Server()` with custom FastAPI routes (`/api/tasks` — CRUD for tasks)
- `@server.api()` for a Gradio-powered AI chat endpoint
- `spa=True` for client-side routing
- Dashboard with stats, Task Manager, and AI Chat — all in one SPA
- Three integration patterns working together in one server

---

## Project Structure

```
gradio-server/
├── gradio/
│   ├── routes.py          # Core: custom_frontend static serving + SPA fallback
│   ├── server.py          # Server class with @server.api() decorator
│   ├── blocks.py          # Blocks.launch() passes custom_frontend/spa through
│   └── ...
├── demo/
│   ├── custom_frontend_static/
│   │   ├── run.py         # Backend: gr.Blocks() + gr.api()
│   │   └── index.html     # Frontend: plain HTML/CSS/JS
│   └── custom_frontend_fullstack/
│       ├── run.py         # Backend: Server() + FastAPI routes + @server.api()
│       └── static/
│           └── index.html # Frontend: SPA with hash routing
├── requirements.txt       # Python dependencies (auto-installed by pip install -e .)
├── pyproject.toml         # Package config
└── README.md
```

---

## Using with React / Vue / Svelte / Next.js

Build your frontend app normally, then point `custom_frontend` at the build output:

```bash
# React example
cd my-react-app
npm run build
# output is in dist/

# In your Gradio backend:
server.launch(custom_frontend="../my-react-app/dist/", spa=True)
```

For **React Router** or **Vue Router** (history mode), set `spa=True` so that all routes fall back to `index.html`.

For **hash-based routing** (`/#/path`), `spa=True` is optional but recommended for consistency.

---

## @server.api() Decorator

The `@server.api()` decorator registers a function as a Gradio API endpoint with full queue support:

```python
@server.api(
    name="chat",              # API endpoint name: /gradio_api/call/chat
    description="Chat with AI",
    concurrency_limit=5,      # Max concurrent requests
    time_limit=30,            # Timeout in seconds
    stream_every=0.5,         # SSE stream interval
    queue=True,               # Use Gradio's queue (default)
    api_visibility="public",  # Show in /gradio_api/
)
def ai_chat(message: str) -> str:
    return process(message)
```

**Parameters:**
| Parameter | Type | Default | Description |
|---|---|---|---|
| `name` | str | None | API endpoint name |
| `description` | str | None | Endpoint description |
| `concurrency_limit` | int \| "default" | "default" | Max concurrent requests |
| `concurrency_id` | str | None | Shared concurrency group ID |
| `queue` | bool | True | Use Gradio's queue system |
| `batch` | bool | False | Enable batching |
| `max_batch_size` | int | 4 | Max batch size |
| `time_limit` | int | None | Request timeout in seconds |
| `stream_every` | float | 0.5 | SSE streaming interval |
| `api_visibility` | "public" \| "private" \| "undocumented" | "public" | Visibility in API docs |

---

## Security

- **Path traversal protection**: The custom frontend catchall route rejects paths containing `..`, prevents access outside the frontend directory, and blocks internal Gradio routes.
- **Internal route guards**: Paths starting with `api`, `docs`, `redoc`, `openapi` are excluded from the SPA fallback to prevent conflicts with FastAPI's built-in routes.
- **CORS**: Use `strict_cors=False` in `launch()` if your frontend is served from a different origin during development.

---

## Requirements

- Python 3.10+
- Dependencies are auto-installed via `pip install -e .` (see `requirements.txt`)

No Node.js or build tools needed unless you're building your own frontend framework app.

---

## License

Based on [Gradio](https://github.com/gradio-app/gradio) — Apache License 2.0