"""
Demo: Fullstack app with Gradio as the backend.

This shows THREE integration patterns in one app:

1. **Custom FastAPI routes** — standard REST endpoints (/api/tasks)
   added directly on the Server instance (which IS a FastAPI app).

2. **Gradio API endpoints** — functions registered with @server.api()
   get full queue + SSE streaming via /gradio_api/*.

3. **Custom static frontend** — a single-page app (HTML/CSS/JS) that
   calls BOTH the custom REST routes and the Gradio API endpoints.

The `spa=True` flag enables client-side routing (hash-based) so that
navigating to /#/tasks, /#/ai, etc. all serve index.html.

Run (after cloning and installing):
    pip install -e .
    python demo/custom_frontend_fullstack/run.py
"""

import os

import gradio as gr
from gradio import Server

# ── In-memory task store (replace with a real DB in production) ──
tasks: list[dict] = [
    {"id": 1, "title": "Learn Gradio custom frontend", "done": False},
    {"id": 2, "title": "Build a fullstack app", "done": False},
]
_next_id = 3


server = Server(
    title="My Fullstack App",
    description="A fullstack application using Gradio as the backend API engine",
    version="1.0.0",
    docs_url="/docs",
)

# ── Custom REST API routes (standard FastAPI) ────────────────────
# These live alongside the Gradio API — no conflict.

from fastapi import HTTPException
from pydantic import BaseModel


class TaskCreate(BaseModel):
    title: str


@server.get("/api/tasks")
def list_tasks():
    """List all tasks (custom FastAPI route)."""
    return tasks


@server.post("/api/tasks", status_code=201)
def create_task(body: TaskCreate):
    """Create a new task (custom FastAPI route)."""
    global _next_id
    task = {"id": _next_id, "title": body.title, "done": False}
    tasks.append(task)
    _next_id += 1
    return task


@server.post("/api/tasks/{task_id}/complete")
def complete_task(task_id: int):
    """Mark a task as done (custom FastAPI route)."""
    for t in tasks:
        if t["id"] == task_id:
            t["done"] = True
            return t
    raise HTTPException(status_code=404, detail="Task not found")


@server.delete("/api/tasks/{task_id}")
def delete_task(task_id: int):
    """Delete a task (custom FastAPI route)."""
    for i, t in enumerate(tasks):
        if t["id"] == task_id:
            tasks.pop(i)
            return {"ok": True}
    raise HTTPException(status_code=404, detail="Task not found")


# ── Gradio-powered AI endpoints (with queue + SSE streaming) ────


@server.api(name="chat")
def ai_chat(message: str) -> str:
    """A simple AI chat function. In production, plug in an LLM here."""
    message_lower = message.lower()
    if "hello" in message_lower or "hi" in message_lower:
        return "Hello! How can I help you today?"
    if "gradio" in message_lower:
        return "Gradio is awesome! It's powering this entire backend — queue, SSE streaming, and file uploads — while the custom frontend handles the UI."
    if "task" in message_lower:
        return f"You currently have {len(tasks)} tasks. Keep going!"
    return f"You said: {message}. This response was processed through Gradio's queue with SSE streaming!"


# ── Launch with the custom frontend ──────────────────────────────

if __name__ == "__main__":
    frontend_dir = os.path.join(os.path.dirname(__file__), "static")
    server.launch(
        custom_frontend=frontend_dir,
        spa=True,  # Enable SPA routing for hash-based navigation
        server_name="0.0.0.0",
        server_port=7860,
        _frontend=False,
    )