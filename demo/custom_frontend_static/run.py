"""
Demo: Static HTML client with Gradio as a pure backend API server.

index.html lives RIGHT NEXT TO this run.py — no separate frontend folder needed.
The _SAFE_EXTENSIONS filter in routes.py ensures .py, .env, .git files
can never be served over HTTP, so it's safe to point custom_frontend at ".".

Run (after cloning and installing):
    pip install -e .
    python demo/custom_frontend_static/run.py
"""

import os

from gradio import Server

server = Server(
    title="Static Frontend Demo",
    description="Gradio as a pure backend API server with a custom static frontend",
)


@server.api(name="reverse")
def reverse(text: str) -> str:
    """Simple API: reverse the input text."""
    return text[::-1]


@server.api(name="echo")
def echo(message: str) -> str:
    """Simple API: echo the message back."""
    return f"Echo: {message}"


if __name__ == "__main__":
    # Serve from the same directory as this script — index.html, style.css,
    # app.js etc. can all live right here alongside run.py.
    # "." resolves relative to CWD, so we use __file__ to be explicit.
    server.launch(
        custom_frontend=os.path.dirname(os.path.abspath(__file__)),
        server_name="0.0.0.0",
        server_port=7860,
        _frontend=False,
    )