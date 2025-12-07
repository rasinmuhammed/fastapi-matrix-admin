# Getting Started

Ready to enter the Matrix? Let's get your admin panel running in under 2 minutes.

## 📦 Installation

This is a pure Python package. No Node.js, no `npm`, no build steps.

```bash
pip install fastapi-matrix-admin
```

> **Note**: We recommend using `uvicorn[standard]` for production-grade async performance.

## 🔌 Integration

### 1. Basic Setup

Add `MatrixAdmin` to your FastAPI app. You need an `AsyncEngine` from SQLAlchemy 1.4+.

```python
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine
from fastapi_matrix_admin import MatrixAdmin

app = FastAPI()
engine = create_async_engine("sqlite+aiosqlite:///db.sqlite3")

admin = MatrixAdmin(
    app,
    engine=engine,
    secret_key="your-super-secret-key-must-be-long",
    title="Matrix HQ"
)
```

### 2. Registering Models

You have two choices: **The Red Pill** (Manual) or **The Blue Pill** (Auto-Magic).

#### The Blue Pill (Auto-Discovery) 💊

Simply pass your SQLAlchemy `Base` class, and we'll find everything.

```python
from models import Base

# Finds all models strictly inheriting from Base
admin.auto_discover(Base)
```

#### The Red Pill (Manual Registration) 💊

For total control over icons, visible columns, and filters.

```python
from fastapi_matrix_admin.core.registry import ModelConfig
from models import User

admin.register(
    User,
    ModelConfig(
        model=User,
        icon="shield",  # Lucide icon name
        list_display=["id", "username", "email", "is_active"],
        searchable_fields=["username", "email"],
        filter_fields=["is_active"]
    )
)
```

## 🏃‍♂️ Running It

Start your FastAPI app as usual:

```bash
uvicorn main:app --reload
```

Navigate to `http://localhost:8000/admin`. 

**Welcome to the Matrix.** 🕶️
