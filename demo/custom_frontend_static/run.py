"""
Demo: Static HTML client with Gradio as a pure backend API server.

The custom_frontend directory contains a plain HTML/CSS/JS website
that calls the Gradio backend API (/gradio_api/*) directly.
No Gradio UI is rendered — only the custom static site is shown.

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
    frontend_dir = os.path.join(os.path.dirname(__file__))
    server.launch(
        custom_frontend=frontend_dir,
        server_name="0.0.0.0",
        server_port=7860,
        _frontend=False,
    )