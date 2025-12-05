"""
Authentication and Authorization for FastAPI Shadcn Admin.

Provides user authentication, session management, and RBAC (Role-Based Access Control).
"""

from __future__ import annotations

from typing import Optional, List
from datetime import datetime, timedelta
import secrets
import hashlib

from sqlalchemy import String, Boolean, Integer, DateTime, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from pydantic import BaseModel, ConfigDict, EmailStr


# --- SQLAlchemy Models ---


class AdminUser(DeclarativeBase):
    """
    Admin user model with authentication and RBAC.

    This model MUST be used if you want built-in authentication.

    Usage:
        from fastapi_shadcn_admin.auth.models import AdminUser
        from sqlalchemy.orm import declarative_base

        Base = declarative_base()

        class User(AdminUser, Base):
            __tablename__ = "admin_users"
    """

    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))

    # RBAC
    roles: Mapped[List[str]] = mapped_column(
        JSON, default=list
    )  # ["admin", "editor", "viewer"]
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    def has_role(self, role: str) -> bool:
        """Check if user has a specific role."""
        if self.is_superuser:
            return True
        roles = self.roles if self.roles is not None else []
        return role in roles

    def has_any_role(self, roles: List[str]) -> bool:
        """Check if user has any of the specified roles."""
        if self.is_superuser:
            return True
        return any(self.has_role(role) for role in roles)

    @classmethod
    def hash_password(cls, password: str) -> str:
        """Hash a password using SHA-256 with salt."""
        salt = secrets.token_hex(32)
        pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}${pwd_hash}"

    def verify_password(self, password: str) -> bool:
        """Verify a password against the stored hash."""
        try:
            salt, pwd_hash = self.password_hash.split("$")
            check_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return check_hash == pwd_hash
        except (ValueError, AttributeError):
            return False

    def update_last_login(self) -> None:
        """Update last login timestamp."""
        self.last_login = datetime.utcnow()


# --- Pydantic Schemas ---


class LoginRequest(BaseModel):
    """Login request schema."""

    username: str
    password: str
    remember_me: bool = False


class UserResponse(BaseModel):
    """User response model for API."""

    id: int
    username: str
    email: EmailStr
    is_active: bool
    is_superuser: bool
    roles: list[str] = []
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CreateUserRequest(BaseModel):
    """Create admin user request."""

    username: str
    email: EmailStr
    password: str
    roles: List[str] = []
    is_superuser: bool = False


# --- Permission System ---


class Permission:
    """Permission constants."""

    VIEW = "view"
    CREATE = "create"
    EDIT = "edit"
    DELETE = "delete"

    @classmethod
    def all(cls) -> List[str]:
        """Get all permissions."""
        return [cls.VIEW, cls.CREATE, cls.EDIT, cls.DELETE]


class PermissionChecker:
    """
    Check user permissions for models.

    Usage:
        checker = PermissionChecker(user, model_config)
        if not checker.can_view():
            raise HTTPException(403)
    """

    def __init__(self, user: Optional[AdminUser], model_permissions: dict):
        """
        Initialize permission checker.

        Args:
            user: Current admin user (None if not authenticated)
            model_permissions: Dict of permission -> list of roles
                Example: {"view": ["*"], "create": ["admin", "editor"]}
        """
        self.user = user
        self.permissions = model_permissions

    def _check(self, permission: str) -> bool:
        """Check if user has a specific permission."""
        if not self.user or not self.user.is_active:
            return False

        if self.user.is_superuser:
            return True

        allowed_roles = self.permissions.get(permission, [])

        # "*" means all authenticated users
        if "*" in allowed_roles:
            return True

        return self.user.has_any_role(allowed_roles)

    def can_view(self) -> bool:
        """Check if user can view records."""
        return self._check(Permission.VIEW)

    def can_create(self) -> bool:
        """Check if user can create records."""
        return self._check(Permission.CREATE)

    def can_edit(self) -> bool:
        """Check if user can edit records."""
        return self._check(Permission.EDIT)

    def can_delete(self) -> bool:
        """Check if user can delete records."""
        return self._check(Permission.DELETE)


# --- Session Management ---


class SessionData(BaseModel):
    """Session data stored in cookie."""

    user_id: int
    username: str
    roles: List[str]
    is_superuser: bool
    expires_at: datetime

    def is_expired(self) -> bool:
        """Check if session is expired."""
        return datetime.utcnow() > self.expires_at

    @classmethod
    def create(
        cls,
        user: AdminUser,
        remember_me: bool = False,
    ) -> "SessionData":
        """Create session data from user."""
        expiry_hours = 720 if remember_me else 24  # 30 days or 1 day
        expires_at = datetime.utcnow() + timedelta(hours=expiry_hours)

        return cls(
            user_id=user.id,
            username=user.username,
            roles=user.roles,
            is_superuser=user.is_superuser,
            expires_at=expires_at,
        )
