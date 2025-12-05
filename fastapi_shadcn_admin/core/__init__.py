"""Core module for FastAPI Shadcn Admin"""

from fastapi_shadcn_admin.core.admin import ShadcnAdmin
from fastapi_shadcn_admin.core.registry import AdminRegistry, ModelConfig
from fastapi_shadcn_admin.core.security import URLSigner, CSPMiddleware
from fastapi_shadcn_admin.core.integrator import SchemaWalker, FieldDefinition

__all__ = [
    "ShadcnAdmin",
    "AdminRegistry",
    "ModelConfig",
    "URLSigner",
    "CSPMiddleware",
    "SchemaWalker",
    "FieldDefinition",
]
