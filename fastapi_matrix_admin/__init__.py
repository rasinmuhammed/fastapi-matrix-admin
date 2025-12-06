"""
FastAPI Shadcn Admin - Zero-Node.js, Pydantic-First Admin Interface
"""

from fastapi_matrix_admin.core.admin import MatrixAdmin
from fastapi_matrix_admin.core.registry import AdminRegistry, ModelConfig
from fastapi_matrix_admin.core.security import URLSigner, CSPMiddleware

__version__ = "0.1.0"

__all__ = [
    "MatrixAdmin",
    "AdminRegistry",
    "ModelConfig",
    "URLSigner",
    "CSPMiddleware",
]
