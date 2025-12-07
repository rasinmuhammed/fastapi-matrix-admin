# Welcome to the Matrix

<div align="center">
  <h1>⚡ FastAPI Matrix Admin</h1>
  <p>
    <strong>The most striking admin panel for FastAPI.</strong><br>
    Terminal-style cyberpunk aesthetics meet production-ready functionality.
  </p>
  <p>
    <a href="https://badge.fury.io/py/fastapi-matrix-admin"><img src="https://badge.fury.io/py/fastapi-matrix-admin.svg" alt="PyPI version"></a>
    <a href="https://github.com/rasinmuhammed/fastapi-matrix-admin/actions/workflows/tests.yml"><img src="https://github.com/rasinmuhammed/fastapi-matrix-admin/workflows/Tests/badge.svg" alt="Tests"></a>
    <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  </p>
</div>

---

## 🕶️ Why Matrix Admin?

Most admin panels are boring. They look like spreadsheets. 

**FastAPI Matrix Admin** is different. It's built for developers who live in the terminal. It's designed to make your backend look as powerful as it feels.

### Core Philosophy

1.  **Aesthetics Matter**: A tool you enjoy looking at is a tool you enjoy using. The "Matrix" theme isn't just a skin; it's an identity.
2.  **Zero Friction**: One line of code [`admin.auto_discover(Base)`] should be enough to start.
3.  **No Node.js**: We love JavaScript, but not in our Python backend build pipeline. This is pure Python.
4.  **Bulletproof**: Production-ready security (CSP, CSRF, Signed URLs) and performance (Async, Eager Loading).

---

## 🚀 Key Features

- **🎨 Matrix UI Theme**: Terminal-style monospace fonts, neon glow effects, and a dark mode that actually looks reliable.
- **🔍 Smart Auto-Discovery**: Automatically finds all your SQLAlchemy models and builds a CRUD interface.
- **🔮 Smart Relationships**: Foreign keys? Many-to-One? We detect them and render searchable dropdowns automatically.
- **⚡ Supercharged Performance**: Built on `SQLAlchemy` async operations with intelligent N+1 query prevention.
- **🛡️ Enterprise Security**: Built-in support for Argon2 hashing, rate limiting, and secure session management.

---

## 🏁 Quick Start

```python
from fastapi import FastAPI
from fastapi_matrix_admin import MatrixAdmin
from settings import engine, Base

app = FastAPI()

# 1. Initialize
admin = MatrixAdmin(app, engine=engine, secret_key="secure-key")

# 2. Revolutions
admin.auto_discover(Base)
```

[Get Started →](guide/getting-started.md){ .md-button .md-button--primary } [View Features →](features.md){ .md-button }
