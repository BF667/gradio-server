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

import gradio as gr


def reverse(text: str) -> str:
    """Simple API: reverse the input text."""
    return text[::-1]


def echo(message: str) -> str:
    """Simple API: echo the message back."""
    return f"Echo: {message}"


# Build a minimal Blocks with only API endpoints (no visible UI).
# gr.api() registers functions that derive their types from type hints
# and are callable via /gradio_api/call/<name>.
with gr.Blocks() as demo:
    gr.api(reverse, api_name="reverse")
    gr.api(echo, api_name="echo")


if __name__ == "__main__":
    frontend_dir = os.path.join(os.path.dirname(__file__))
    demo.launch(
        custom_frontend=frontend_dir,
        server_name="0.0.0.0",
        server_port=7860,
        _frontend=False,  # don't open browser iframe
    )