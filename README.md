# ⚡ FastAPI Matrix Admin

<div align="center">
  <img src="https://raw.githubusercontent.com/rasinmuhammed/fastapi-matrix-admin/main/docs/assets/banner.png" alt="FastAPI Matrix Admin" width="100%">
  <br>
  <h3>Enter the Matrix. Your backend never looked this good.</h3>
</div>

<p align="center">
  <a href="https://badge.fury.io/py/fastapi-matrix-admin"><img src="https://badge.fury.io/py/fastapi-matrix-admin.svg" alt="PyPI version"></a>
  <a href="https://github.com/rasinmuhammed/fastapi-matrix-admin/actions/workflows/tests.yml"><img src="https://github.com/rasinmuhammed/fastapi-matrix-admin/workflows/Tests/badge.svg" alt="Tests"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
</p>

---

**FastAPI Matrix Admin** is a "battery-included" admin panel built for the modern Python stack. It combines the raw power of **Async SQLAlchemy** with a stunning **Terminal-style Cyberpunk UI**.

> "Most admin panels are boring spreadsheets. This one makes you feel like a hacker."

### 🌟 Why this exists?

- **Zero Node.js**: No `npm`, no `webpack`. Pure Python.
- **Aesthetic First**: A dark mode that actually looks professional (Matrix Green/Black).
- **Developer Experience**: One-line auto-discovery for all your models.
- **Performance**: Built for high-concurrency async applications.

---

## 🚀 Key Features

| Feature | Description |
|---------|-------------|
| **🔮 Smart Selects** | Automatically turns Foreign Keys into searchable AJAX dropdowns. |
| **🧪 Advanced Filters** | Sidebar filters for booleans, dates, relationships, and custom operators. |
| **📊 Observability** | Real-time Dashboard with CPU, RAM, and Disk metrics. |
| **💾 Streaming Export** | Export massive datasets to CSV without crashing memory. |
| **🛡️ Bulletproof Auth** | Secure, session-based authentication with Argon2 hashing. |

---

## 📦 Quick Start

### 1. Install

```bash
pip install fastapi-matrix-admin
```

### 2. Plug & Play

```python
from fastapi import FastAPI
from fastapi_matrix_admin import MatrixAdmin
from models import Base, engine

app = FastAPI()

# Initialize
admin = MatrixAdmin(app, engine=engine, secret_key="secure-key")

# The Magic Line ✨
admin.auto_discover(Base)
```

### 3. Create Admin User

Use the built-in utility to create your first superuser:

```python
from fastapi_matrix_admin.auth.utils import create_superuser

# In your startup script
async def create_admin():
    async with engine.begin() as conn:
        await create_superuser(conn, User, "admin", "admin@example.com", "secure-password")
```

[Read the Full Documentation →](https://rasinmuhammed.github.io/fastapi-matrix-admin/)

---

## 🎯 Live Demo

Experience the revolution yourself.

**[👉 Launch Live Demo](https://fastapi-matrix-admin-demo.onrender.com/admin/)**

*(Credentials: `admin` / `admin`)*

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
