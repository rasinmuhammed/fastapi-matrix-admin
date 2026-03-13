"""FastAPI Matrix Admin public package exports."""

from fastapi_matrix_admin.core.admin import MatrixAdmin
from fastapi_matrix_admin.core.registry import AdminRegistry, ModelConfig
from fastapi_matrix_admin.core.security import URLSigner, CSPMiddleware
from fastapi_matrix_admin.core.views import (
    AdminAction,
    DashboardCard,
    DetailPanel,
    ModelAdmin,
)

__version__ = "1.1.0"

__all__ = [
    "MatrixAdmin",
    "AdminRegistry",
    "ModelConfig",
    "ModelAdmin",
    "AdminAction",
    "DetailPanel",
    "DashboardCard",
    "URLSigner",
    "CSPMiddleware",
]
