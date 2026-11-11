"""
Containerized Python API - FastAPI Application
===============================================
This module provides a FastAPI-based REST API with the following features:
- A welcome endpoint that greets the user by name
- A token generation endpoint (single token)
- A checksum generation endpoint (accepts text, returns checksum)

Author: Lab Participant
Framework: FastAPI
"""

import hashlib
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel


# ---------------------------------------------------------------------------
# FastAPI app instance
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Containerized Python API",
    description=(
        "This is a containerized application that exposes a JSON API using "
        "FastAPI with Uvicorn. It provides token generation and checksum "
        "utilities."
    ),
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Pydantic model for the /generate endpoint
# Accepts a JSON body with a single 'text' field
# ---------------------------------------------------------------------------
class TextInput(BaseModel):
    """
    Request body model for text-based endpoints.

    Attributes:
        text (str): The input string that will be processed by the API.
    """
    text: str


# ---------------------------------------------------------------------------
# Utility / core function
# ---------------------------------------------------------------------------
def generate(text: str) -> str:
    """
    Generate a SHA-256 checksum (hex digest) for the provided text.

    Args:
        text (str): The input string to hash.

    Returns:
        str: A 64-character hexadecimal SHA-256 digest of the input text.

    Example:
        >>> generate("hello")
        '2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824'
    """
    return hashlib.sha256(text.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Root / Welcome endpoint
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse, tags=["Welcome"])
def welcome():
    """
    Welcome endpoint.

    Returns an HTML page that greets the participant by name and provides
    links to the interactive API documentation and the project source.

    Returns:
        HTMLResponse: A styled HTML page with a welcome message.
    """
    participant_name = "Jaya Narayana"  # ← Replace with your name

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
        <title>Containerized Python API</title>
        <style>
            body {{
                background-color: #1e1e2e;
                color: #cdd6f4;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
                margin: 0;
                padding: 2rem;
                box-sizing: border-box;
            }}
            .card {{
                background: #313244;
                border-radius: 12px;
                padding: 2.5rem 3rem;
                max-width: 600px;
                width: 100%;
                text-align: center;
                box-shadow: 0 8px 32px rgba(0,0,0,0.4);
            }}
            h1 {{ color: #cba6f7; margin-bottom: 0.5rem; }}
            .quote {{ font-style: italic; color: #a6e3a1; margin: 1rem 0 2rem; }}
            .rocket {{ font-size: 4rem; margin: 1rem 0; }}
            h2 {{ color: #89b4fa; }}
            p {{ color: #bac2de; line-height: 1.6; }}
            .btn-row {{ display: flex; gap: 1rem; justify-content: center; margin-top: 1.5rem; }}
            a.btn {{
                padding: 0.5rem 1.25rem;
                border-radius: 6px;
                text-decoration: none;
                font-weight: 600;
                font-size: 0.9rem;
            }}
            .btn-primary {{ background: #cba6f7; color: #1e1e2e; }}
            .btn-secondary {{ background: #45475a; color: #cdd6f4; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Welcome to the webpage, {participant_name}!</h1>
            <p class="quote">
                "The only way to do great work is to love what you do." — Steve Jobs
            </p>
            <div class="rocket">🚀</div>
            <h2>Containerized Python API</h2>
            <p>
                This is a containerized application that exposes a JSON API using
                <strong>FastAPI</strong> with <strong>Uvicorn</strong>.<br/>
                Use the buttons below to try out the interactive (OpenAPI) documentation
                or browse the project source.
            </p>
            <div class="btn-row">
                <a class="btn btn-primary" href="/docs">Try it out</a>
                <a class="btn btn-secondary" href="/redoc">Project source</a>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


# ---------------------------------------------------------------------------
# Single-token generation endpoint (original)
# ---------------------------------------------------------------------------
@app.get(
    "/token",
    tags=["Token"],
    summary="Generate a single token",
    response_description="A single SHA-256 token derived from a fixed seed.",
)
def get_token():
    """
    Generate a single deterministic token.

    This endpoint uses the fixed seed string ``"token"`` and returns its
    SHA-256 hex digest.  Useful for verifying that the hashing utility is
    working correctly.

    Returns:
        dict: ``{"token": "<64-char hex string>"}``
    """
    return {"token": generate("token")}


# ---------------------------------------------------------------------------
# New endpoint: accepts text, returns its SHA-256 checksum
# ---------------------------------------------------------------------------
@app.post(
    "/generate",
    tags=["Generate"],
    summary="Generate a checksum for the provided text",
    response_description="A SHA-256 checksum of the supplied text.",
)
def generate_checksum(payload: TextInput):
    """
    Accept a JSON body containing a ``text`` field and return its
    SHA-256 checksum.

    **Request body example**
    ```json
    { "text": "Hello, World!" }
    ```

    **Response example**
    ```json
    {
        "text": "Hello, World!",
        "checksum": "dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986d"
    }
    ```

    Args:
        payload (TextInput): JSON body with a single ``text`` field.

    Returns:
        dict: Original text and its corresponding SHA-256 checksum.
    """
    checksum = generate(payload.text)
    return {"text": payload.text, "checksum": checksum}
