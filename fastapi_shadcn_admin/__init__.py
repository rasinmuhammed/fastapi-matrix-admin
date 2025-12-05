"""
FastAPI Shadcn Admin - Zero-Node.js, Pydantic-First Admin Interface
"""

from fastapi_shadcn_admin.core.admin import ShadcnAdmin
from fastapi_shadcn_admin.core.registry import AdminRegistry, ModelConfig
from fastapi_shadcn_admin.core.security import URLSigner, CSPMiddleware

__version__ = "0.1.0"

__all__ = [
    "ShadcnAdmin",
    "AdminRegistry",
    "ModelConfig",
    "URLSigner",
    "CSPMiddleware",
]
