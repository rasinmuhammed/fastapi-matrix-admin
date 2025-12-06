# ⚡ FastAPI Matrix Admin

> **Enter the Matrix** - The most striking admin panel for FastAPI. Terminal-style cyberpunk aesthetics meet production-ready functionality.

[![PyPI version](https://badge.fury.io/py/fastapi-matrix-admin.svg)](https://badge.fury.io/py/fastapi-matrix-admin)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://github.com/rasinmuhammed/fastapi-matrix-admin/workflows/Tests/badge.svg)](https://github.com/rasinmuhammed/fastapi-matrix-admin/actions/workflows/tests.yml)
[![Code Quality](https://github.com/rasinmuhammed/fastapi-matrix-admin/workflows/Code%20Quality/badge.svg)](https://github.com/rasinmuhammed/fastapi-matrix-admin/actions/workflows/quality.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Zero Node.js** • **Matrix UI Theme** • **Terminal Aesthetics** • **One-Line Auto-Discovery**

## 🎯 Live Demo

**[👉 Try the Live Demo →](https://fastapi-matrix-admin.onrender.com/admin/)**

Experience the Matrix:
- ⚡ **Matrix Green/Black Theme** - Terminal-style design with neon glow effects
- 🔍 **Auto-Discovery** - 4 models registered with one line of code
- 📝 **Full CRUD** - Create, Read, Update, Delete with smooth animations
- 🎨 **Cyberpunk Aesthetics** - Glassmorphism, micro-interactions, monospace fonts
- ⚡ **Pre-seeded Data** - Ready to explore immediately

**Run Locally:**
```bash
git clone https://github.com/rasinmuhammed/fastapi-matrix-admin.git
cd fastapi-matrix-admin/demo
pip install -r requirements.txt
python app.py
# Visit http://localhost:8000/admin
```

---

## ✨ Why FastAPI Matrix Admin?

```python
# Literally this simple:
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine
from fastapi_matrix_admin import MatrixAdmin

app = FastAPI()
engine = create_async_engine("postgresql+asyncpg://...")

admin = MatrixAdmin(app, engine=engine, secret_key="your-secret")
admin.auto_discover(Base)  # ✨ Magic! All models registered

# Visit /admin - Full Matrix-themed admin panel!
```

### What Makes It Different?

**🎨 Unique Matrix Aesthetic**
- No other FastAPI admin looks like this
- Terminal-style monospace fonts
- Green/black cyberpunk theme
- Neon glow effects on interactive elements
- Makes your backend look as cool as your frontend

**⚡ Zero Node.js**
- Pure Python - no npm, no webpack, no build step
- Just `pip install fastapi-matrix-admin`
- Tailwind CSS via CDN
- HTMX for dynamic interactions

**🔍 Auto-Discovery**
- One line: `admin.auto_discover(Base)`
- Automatically finds all SQLAlchemy models
- Smart defaults for list views, search, and forms
- No configuration needed (but fully customizable)

**🛡️ Production-Ready**
- Async SQLAlchemy 2.0
- Pydantic v2 validation
- CSP middleware
- CSRF protection
- URL signing for security

---

## 📦 Installation

```bash
pip install fastapi-matrix-admin
```

---

## 🚀 Quick Start

### Minimal Example

```python
from fastapi import FastAPI
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from fastapi_matrix_admin import Matrix Admin

# Your SQLAlchemy models
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)

# FastAPI app
appFastAPI()
engine = create_async_engine("sqlite+aiosqlite:///./database.db")

# Matrix Admin - One line setup!
admin = MatrixAdmin(app, engine=engine, secret_key="your-secret-key-min-32-chars")
admin.auto_discover(Base)

# Run: uvicorn app:app
# Visit: http://localhost:8000/admin
```

### With Customization

```python
# Register models with custom configuration
admin.register(
    User,
    list_display=["id", "name", "email", "created_at"],
    searchable_fields=["name", "email"],
    ordering=["-created_at"],
    icon="user",
)

# Or use auto-discovery with filters
admin.auto_discover(
    Base,
    include=["User", "Post", "Comment"],  # Only these models
    exclude=["InternalModel"]  # Skip these
)
```

---

## 🎨 Features

### Core Features
- ✅ **Full CRUD Operations** - Create, Read, Update, Delete
- ✅ **Auto-Discovery** - Automatically register SQLAlchemy models
- ✅ **List Views** - Pagination, sorting, searching, filtering
- ✅ **Form Generation** - Auto-generated forms from models
- ✅ **Relationships** - Foreign keys, many-to-many support
- ✅ **Validation** - Pydantic v2 schemas
- ✅ **Async First** - SQLAlchemy 2.0 async

### Matrix UI Features
- ⚡ **Terminal Aesthetic** - Monospace fonts, command-line feel
- 🎨 **Neon Glow Effects** - Interactive elements pulse with green light
- 🖥️ **Glassmorphism** - Modern blur effects and translucent cards
- ⚙️ **Smooth Animations** - Micro-interactions throughout
- 📱 **Fully Responsive** - Works on mobile, tablet, desktop

### Security Features
- 🛡️ **CSP Middleware** - Content Security Policy protection
- 🔐 **URL Signing** - Cryptographically signed URLs
- 🔒 **CSRF Protection** - Cross-Site Request Forgery prevention
- ✅ **Type Safety** - Full type hints with Pydantic

---

## 📚 Documentation

### Configuration Options

```python
admin = MatrixAdmin(
    app,                    # FastAPI application
    engine=engine,          # SQLAlchemy async engine
    secret_key="...",       # Secret key for signing (min 16 chars)
    title="Admin",          # Panel title (default: "Admin")
    prefix="/admin",        # URL prefix (default: "/admin")
    add_csp_middleware=True,  # Add CSP (default: True)
    max_recursion_depth=5,  # Schema walking depth (default: 5)
)
```

### Model Registration

```python
from fastapi_matrix_admin import MatrixAdmin

# Basic registration
admin.register(User)

# With all options
admin.register(
    User,
    name="Users",                    # Display name
    list_display=["id", "email"],    # Columns in list view
    searchable_fields=["email"],    # Searchable fields
    ordering=["-created_at"],        # Default ordering
    icon="user",                     # Sidebar icon
    fields=["name", "email"],        # Form fields to include
    exclude=["password_hash"],       # Fields to hide
    readonly=False,                  # Make read-only
)
```

### Auto-Discovery

```python
# Discover all models
admin.auto_discover(Base)

# With filters
admin.auto_discover(
    Base,
    include=["User", "Post"],  # Only these
    exclude=["Internal"]       # Skip these
)
```

---

## 🎯 Examples

See the `/examples` directory for complete working examples:
- **demo.py** - Basic SQLAlchemy setup
- **demo_auto.py** - Auto-discovery showcase
- **demo_db.py** - PostgreSQL example

---

## 🛠️ Development

```bash
# Clone
git clone https://github.com/rasinmuhammed/fastapi-matrix-admin.git
cd fastapi-matrix-admin

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Code quality
black .
ruff check .
```

---

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📜 License

MIT License - see [LICENSE](LICENSE.md)

---

## 🌟 Star History

If you find this project useful, give it a ⭐!

---

## 💬 Support

- 📖 [Documentation](https://github.com/rasinmuhammed/fastapi-matrix-admin#readme)
- 🐛 [Bug Reports](https://github.com/rasinmuhammed/fastapi-matrix-admin/issues)
- 💡 [Feature Requests](https://github.com/rasinmuhammed/fastapi-matrix-admin/issues)

---

<div align="center">

**Made with ⚡ by FastAPI Matrix Admin contributors**

*Enter the Matrix. Your backend never looked this good.*

</div>
