"""Core module for FastAPI Shadcn Admin"""

from fastapi_matrix_admin.core.admin import MatrixAdmin
from fastapi_matrix_admin.core.registry import AdminRegistry, ModelConfig
from fastapi_matrix_admin.core.security import URLSigner, CSPMiddleware
from fastapi_matrix_admin.core.integrator import SchemaWalker, FieldDefinition

__all__ = [
    "MatrixAdmin",
    "AdminRegistry",
    "ModelConfig",
    "URLSigner",
    "CSPMiddleware",
    "SchemaWalker",
    "FieldDefinition",
]
