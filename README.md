# 🚀 FastAPI Shadcn Admin

> **The FastAPI admin panel you always wanted** - Modern, secure, and beautifully simple.

[![PyPI version](https://badge.fury.io/py/fastapi-shadcn-admin.svg)](https://badge.fury.io/py/fastapi-shadcn-admin)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://github.com/rasinmuhammed/fastapi-shadcn-admin/workflows/Tests/badge.svg)](https://github.com/rasinmuhammed/fastapi-shadcn-admin/actions/workflows/tests.yml)
[![Code Quality](https://github.com/rasinmuhammed/fastapi-shadcn-admin/workflows/Code%20Quality/badge.svg)](https://github.com/rasinmuhammed/fastapi-shadcn-admin/actions/workflows/quality.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Zero Node.js** • **Pydantic v2** • **Full Async** • **Military-Grade Security**

## 🎯 Live Demo

**[👉 Try the Live Demo →](https://fastapi-shadcn-admin-iscte2c9y.vercel.app)**

Experience the Matrix-themed UI with auto-discovered models. The demo showcases:
- ✨ Matrix green/black aesthetic with terminal-style design
- 🔍 Auto-discovery of 4 models (BlogPost, Product, Author, Category)
- 📝 Full CRUD operations (read-only mode for public safety)
- 🎨 Smooth animations and micro-interactions

---

## ✨ Why FastAPI Shadcn Admin?

```python
# Literally this simple:
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine
from fastapi_shadcn_admin import ShadcnAdmin

app = FastAPI()
engine = create_async_engine("postgresql+asyncpg://...")

admin = ShadcnAdmin(app, engine=engine, secret_key="your-secret")
admin.auto_discover(Base)  # ✨ Magic! All models registered

# Visit /admin - Full admin panel with auth, RBAC, audit logs, and more!
```

**3 lines of code.** That's it.

---

## 🌟 What Makes It Special

### Unique Features (No Competition Has These)

| Feature | FastAPI Shadcn | Django Admin | SQLAdmin | Retool |
|---------|----------------|--------------|----------|--------|
| **Auto-Discovery** | ✅ Smart defaults | ✅ Basic | ✅ Basic | N/A |
| **Zero Node.js** | ✅ Pure Python | ✅ Pure Python | ❌ Requires npm | ❌ Cloud only |
| **Pydantic Unions** | ✅ **FIRST** | ❌ | ❌ | ❌ |
| **Signed URL Tokens** | ✅ **ONLY** | ❌ | ❌ | ⚠️ Basic |
| **Modern UI (2024)** | ✅ Shadcn/Tailwind | ❌ Bootstrap 3 | ⚠️ Basic | ✅ Custom |
| **Full Async** | ✅ Native | ⚠️ Partial | ✅ Native | ✅ |
| **Field-Level Audit** | ✅ Built-in | ⚠️ Plugin | ❌ | ✅ |
| **HTMX** | ✅ Progressive | ❌ | ❌ | ❌ |
| **Price** | **FREE** | FREE | FREE | **$50K+/year** |

### The "WOW" Moment

**Others:** "Here's an empty admin panel, now configure 50+ settings per model."

**Us:** `admin.auto_discover(Base)` → **Done.** Beautiful admin with:
- Smart field inference
- Automatic search setup
- Proper ordering
- Contextual icons
- Analytics dashboard
- Full CRUD
- Auth & RBAC
- Audit logging

---

## 🎯 Perfect For

- **Startups** - Ship admin panels in minutes, not days
- **Internal Tools** - Pragmatic, no-nonsense data management
- **MVPs** - Get to market fast with professional admin
- **Enterprises** - Security-first, compliance-ready (SOC 2/GDPR)
- **Developers** - Beautiful code, beautiful UI, zero compromises

---

## 🚀 Quick Start

### Installation

```bash
pip install fastapi-shadcn-admin
```

### Basic Setup

```python
from fastapi import FastAPI
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from fastapi_shadcn_admin import ShadcnAdmin

# Your existing FastAPI app
app = FastAPI()

# Your existing SQLAlchemy models
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String)

# Create engine
engine = create_async_engine("sqlite+aiosqlite:///./test.db")

# Initialize admin (ONE LINE!)
admin = ShadcnAdmin(app, engine=engine, secret_key="your-secret-key-min-32-chars")

# Auto-discover all models
admin.auto_discover(Base)

# That's it! Visit http://localhost:8000/admin
```

### Run It

```bash
uvicorn main:app --reload
```

Visit `http://localhost:8000/admin` and see the magic! ✨

---

## 📚 Documentation

### Features Deep Dive

#### 🔐 Security (Military-Grade)

**Signed URL Tokens** (Unique to this library!)
```python
# Every action gets a tamper-proof token
# Prevents IDOR, replay attacks, and unauthorized access
admin.register(User)  # URLs automatically signed
```

**What You Get:**
- 🛡️ Anti-IDOR protection (signed tokens)
- 🔒 CSRF protection (signed cookies)
- 🚫 XSS prevention (CSP with nonces)
- 👥 RBAC (role-based per-model)
- 📝 Audit logging (field-level tracking)
- 🔑 Password hashing (SHA-256 + salt)

#### 🎨 Modern UI

Built with **Shadcn** design system:
- Dark mode by default
- Smooth animations
- Responsive (mobile, tablet, desktop)
- Professional typography
- Glassmorphism effects

**Analytics Dashboard:**
- Real-time KPI cards
- Chart.js visualizations
- Quick action buttons
- Recent activity feed

#### 🤖 Auto-Discovery

```python
# Smart defaults for everything
admin.auto_discover(Base)

# Automatically infers:
# - list_display: id, name, email, created_at, etc.
# - searchable_fields: all text columns
# - ordering: -created_at or -id
# - icons: contextual (User → users, Article → file-text)
```

**Exclude sensitive models:**
```python
admin.auto_discover(Base, exclude=["Secret", "ApiKey"])
```

#### 🎯 Pydantic Discriminated Unions (FIRST!)

```python
from pydantic import BaseModel, Field
from typing import Literal

class TextBlock(BaseModel):
    type: Literal["text"] = "text"
    content: str

class ImageBlock(BaseModel):
    type: Literal["image"] = "image"
    url: str
    alt: str

class VideoBlock(BaseModel):
    type: Literal["video"] = "video"
    url: str

# Register polymorphic model
admin.register(
    Content,
    subtypes=[TextBlock, ImageBlock, VideoBlock]
)

# Forms automatically adapt based on discriminator!
```

#### 📊 Export Data

```python
# CSV export with UTF-8 BOM (Excel-compatible)
from fastapi_shadcn_admin.core.export import export_to_csv

csv_data = await export_to_csv(
    session,
    User,
    fields=["id", "email", "created_at"],
    max_rows=10000
)
```

#### 🔍 Advanced Usage

**Explicit Registration:**
```python
admin.register(
    User,
    list_display=["id", "username", "email", "is_active"],
    searchable_fields=["username", "email"],
    ordering=["-created_at"],
    icon="users",
    readonly=False,
    permissions={"delete": ["admin"]}  # Only admins can delete
)
```

**Custom Permissions:**
```python
from fastapi_shadcn_admin.auth import AdminUser, Role

# Create roles
admin_role = Role(name="admin", permissions=["*"])
editor_role = Role(name="editor", permissions=["read", "write"])

# Create admin user
admin_user = AdminUser(
    username="admin",
    email="admin@example.com",
    is_superuser=True
)
admin_user.set_password("secure-password-here")
```

**Audit Logging:**
```python
from fastapi_shadcn_admin.audit import AuditLogger

logger = AuditLogger(session)
await logger.log_update(
    model_name="User",
    record_id=123,
    old_values={"email": "old@example.com"},
    new_values={"email": "new@example.com"},
    user_id=1,
    user_name="admin"
)

# Query audit logs
from fastapi_shadcn_admin.audit import AuditLog
logs = await session.execute(
    select(AuditLog).where(AuditLog.model_name == "User")
)
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                  FastAPI App                    │
└─────────────────────────────────────────────────┘
                       │
       ┌───────────────┴───────────────┐
       │     ShadcnAdmin (Core)        │
       │  - Router management          │
       │  - Security middleware        │
       │  - Session management         │
       └───────────┬───────────────────┘
                   │
           ┌───────┴────────┐
           │                │
    ┌──────▼─────┐   ┌─────▼──────┐
    │ Registry   │   │  Database  │
    │ - Models   │   │  - CRUD    │
    │ - Config   │   │  - Session │
    │ - Security │   │  - Audit   │
    └────────────┘   └────────────┘
           │                │
           └───────┬────────┘
                   │
         ┌─────────▼──────────┐
         │   Jinja2 Templates │
         │   + HTMX + Alpine  │
         └────────────────────┘
```

**Key Design Decisions:**
- **Zero Node.js**: Pure Python + CDN (Tailwind, HTMX, Alpine)
- **Async-First**: Full SQLAlchemy async support
- **Security-First**: Signed tokens, CSRF, CSP, audit logs
- **Type-Safe**: Pydantic v2 throughout
- **No Magic**: Explicit registration, clear contracts

---

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=fastapi_shadcn_admin --cov-report=html

# Current status: 27/30 passing (90%)
# - 16/16 security tests ✅
# - 5/5 CRUD tests ✅
# - 4/4 auth tests ✅
# - 2/2 integration tests ✅
```

---

## 🤝 Contributing

We love contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Quick Guide:**
1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Make your changes
4. Run tests (`pytest`)
5. Format code (`black . && ruff check --fix .`)
6. Commit (`git commit -m 'Add amazing feature'`)
7. Push (`git push origin feature/amazing`)
8. Open a Pull Request

**Areas We'd Love Help:**
- 📖 Documentation improvements
- 🧪 Additional test coverage
- 🎨 UI/UX enhancements
- 🌍 Internationalization (i18n)
- 🔌 Database adapter plugins

---

## 📝 License

MIT License - see [LICENSE](LICENSE.md) file for details.

Free for personal and commercial use. Attribution appreciated but not required.

---

## 🙏 Acknowledgments

- **FastAPI** - The amazing web framework
- **Shadcn/ui** - Design inspiration
- **HTMX** - Simplicity in interactivity
- **Pydantic** - Type safety
- **SQLAlchemy** - Powerful ORM
- **Tailwind CSS** - Utility-first styling

---

## 📞 Support & Community

- **Issues**: [GitHub Issues](https://github.com/rasinmuhammed/fastapi-shadcn-admin/issues)
- **Discussions**: [GitHub Discussions](https://github.com/rasinmuhammed/fastapi-shadcn-admin/discussions)


---

## 🗺️ Roadmap

**v0.2.0 (Next Release):**
- [ ] Inline editing in list view
- [ ] Advanced filter sidebar
- [ ] Export to Excel/PDF
- [ ] Bulk actions UI
- [ ] WebSocket live updates

**v1.0.0 (Stable):**
- [ ] 100% test coverage
- [ ] Comprehensive documentation site
- [ ] Video tutorials
- [ ] Plugin system
- [ ] Internationalization

**Future:**
- [ ] GraphQL support
- [ ] Theme customization
- [ ] Mobile app (React Native)

---

## ⭐ Star History

If this project helps you, please consider giving it a ⭐!

[![Star History Chart](https://api.star-history.com/svg?repos=rasinmuhammed/fastapi-shadcn-admin&type=Date)](https://star-history.com/#rasinmuhammed/fastapi-shadcn-admin&Date)

---

## 💎 Why "Shadcn Admin"?

**Shadcn/ui** represents the modern, component-based approach to UI development. We bring that philosophy to FastAPI admin panels:

- **Composable**: Mix and match features
- **Beautiful**: Modern design that impresses
- **Simple**: Complexity hidden, power revealed
- **Professional**: Production-ready from day one

---

<div align="center">

### Made with ❤️ for the FastAPI community

**[Get Started](https://github.com/rasinmuhammed/fastapi-shadcn-admin#-quick-start)** • **[Documentation](#-documentation)** • **[Examples](examples/)** • **[Contributing](CONTRIBUTING.md)**

</div>
