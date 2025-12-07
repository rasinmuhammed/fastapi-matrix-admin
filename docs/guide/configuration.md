# Configuration

Control the Matrix with precision.

## MatrixAdmin

The main class that initializes the admin interface.

```python
class MatrixAdmin:
    def __init__(
        self,
        app: FastAPI,
        secret_key: str,
        engine: AsyncEngine = None,
        title: str = "Admin",
        prefix: str = "/admin",
        auth_model: Type[DeclarativeBase] = None
    )
```

| Parameter | Type | default | Description |
|-----------|------|---------|-------------|
| `app` | `FastAPI` | Required | Your FastAPI application instance. |
| `secret_key` | `str` | Required | Used for cryptographic signing (sessions, CSRF). |
| `engine` | `AsyncEngine` | `None` | SQLAlchemy async engine. Required for CRUD. |
| `title` | `str` | `"Admin"` | The title displayed in the browser tab and sidebar. |
| `prefix` | `str` | `"/admin"` | The URL prefix for all admin routes. |
| `auth_model` | `class` | `None` | Your User model class for built-in authentication. |

## ModelConfig

Configuration object for fine-tuning how a model is displayed.

```python
@dataclass
class ModelConfig:
    model: Type[BaseModel]
    list_display: list[str] = []
    searchable_fields: list[str] = []
    filter_fields: list[str] = []
    icon: str = "file"
    # ...
```

| Field | Description | Example |
|-------|-------------|---------|
| `list_display` | Columns to show in the table view. | `["id", "name", "email"]` |
| `searchable_fields` | Fields to query when typing in the search bar. | `["username", "email"]` |
| `filter_fields` | Fields to generate sidebar filters for. | `["is_active", "created_at"]` |
| `ordering` | Default sort order. Prefix with `-` for DESC. | `["-created_at"]` |
| `icon` | Name of the Lucide icon to use in the sidebar. | `"users"`, `"shopping-bag"` |
| `readonly` | If `True`, creates a view-only interface. | `True` |

## Authentication

To enable "Bulletproof" authentication, you must provide a user model that inherits from `AdminUser`.

```python
from fastapi_matrix_admin.auth.models import AdminUser

class User(AdminUser, Base):
    __tablename__ = "users"
```

Then pass it during initialization:

```python
admin = MatrixAdmin(..., auth_model=User)
```
