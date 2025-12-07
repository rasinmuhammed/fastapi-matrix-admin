# API Reference

Complete class and function reference.

## Core

### MatrixAdmin

`fastapi_matrix_admin.MatrixAdmin`

The main class that initializes the admin interface.

**Arguments**:

- `app` (FastAPI): Your FastAPI application instance.
- `secret_key` (str): Secret key for signing sessions and URLs. Must be kept secret in production.
- `engine` (AsyncEngine, optional): SQLAlchemy async engine. Required if using database features.
- `title` (str, optional): Admin panel title. Defaults to "Admin".
- `prefix` (str, optional): URL prefix. Defaults to "/admin".
- `auth_model` (Type[AdminUser], optional): User model for authentication.

**Methods**:

- `register(model, config)`: Register a single model manually.
- `auto_discover(base)`: Automatically find and register all models inheriting from the given SQLAlchemy base.

### ModelConfig

`fastapi_matrix_admin.core.registry.ModelConfig`

Configuration dataclass for registered models.

**Attributes**:

- `model`: The SQLAlchemy model class.
- `list_display` (list[str]): Fields to show in the list table.
- `searchable_fields` (list[str]): Fields to include in search queries.
- `filter_fields` (list[str]): Fields to generate sidebar filters for.
- `icon` (str): Lucide icon name (e.g., "user", "file").
- `ordering` (list[str]): Default sorting (e.g., `["-id"]`).
- `readonly` (bool): If True, disables Create/Update/Delete actions.

## Utilities

### URLSigner

`fastapi_matrix_admin.core.security.URLSigner`

Helper to sign and verify URLs to prevent tampering.

- `sign(url)`: Returns a signed URL.
- `verify(token)`: Verifies signatures.

### AuditLogger

`fastapi_matrix_admin.audit.models.AuditLogger`

Handles creation of audit log entries for all admin actions.
