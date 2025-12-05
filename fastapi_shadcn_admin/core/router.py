"""
Admin Router for FastAPI Shadcn Admin.

Implements all admin endpoints with security validation:
- Dashboard and list views
- Create, edit, delete operations
- Signed fragment loading for polymorphic forms
"""

from __future__ import annotations

import math
from typing import Any, TYPE_CHECKING, Callable
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Request, HTTPException, Depends, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

if TYPE_CHECKING:
    from fastapi_shadcn_admin.core.registry import AdminRegistry
    from fastapi_shadcn_admin.core.security import URLSigner
    from fastapi_shadcn_admin.core.integrator import SchemaWalker
    from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_shadcn_admin.core.crud import CRUDBase


def create_admin_router(
    registry: "AdminRegistry",
    signer: "URLSigner",
    walker: "SchemaWalker",
    templates,
    prefix: str = "/admin",
    title: str = "Admin",
    session_dependency: Callable[[], AsyncGenerator["AsyncSession", None]]
    | None = None,
) -> APIRouter:
    """
    Create the admin router with all endpoints.

    Args:
        registry: The AdminRegistry with registered models
        signer: URLSigner for token validation
        walker: SchemaWalker for form field generation
        templates: Jinja2Templates instance
        prefix: URL prefix for admin routes
        title: Admin panel title
        session_dependency: Optional async session dependency for database operations

    Returns:
        Configured APIRouter
    """
    router = APIRouter(tags=["admin"])

    def get_common_context(request: Request) -> dict[str, Any]:
        """Get common template context."""
        return {
            "request": request,
            "admin_title": title,
            "models": registry.get_all(),  # Get model names, not ModelConfig objects
            "csp_nonce": getattr(request.state, "csp_nonce", ""),
        }

    # ==================== Dashboard ====================

    @router.get("/", response_class=HTMLResponse, name="admin:index")
    async def dashboard(
        request: Request,
        session: "AsyncSession" = Depends(session_dependency)
        if session_dependency
        else None,
    ):
        """Admin dashboard with analytics."""
        from datetime import datetime, timedelta
        from sqlalchemy import func, select

        # Get registered models
        registered_models = registry.get_all()  # Returns list of model names

        # Calculate KPIs
        kpis = []
        model_counts = {}

        if session and session_dependency:
            # Count records per model
            for model_name in registered_models:
                try:
                    config = registry.get(model_name)
                    if hasattr(config.model, "__tablename__"):
                        result = await session.execute(
                            select(func.count()).select_from(config.model)
                        )
                        count = result.scalar() or 0
                        model_counts[model_name] = count
                except Exception:
                    model_counts[model_name] = 0

            # Total records KPI
            total_records = sum(model_counts.values())
            kpis.append(
                {
                    "label": "Total Records",
                    "value": f"{total_records:,}",
                    "icon": "database",
                    "change": None,
                }
            )

            # Models KPI
            kpis.append(
                {
                    "label": "Models",
                    "value": len(registered_models),
                    "icon": "layers",
                    "change": None,
                }
            )
        else:
            # No database - show model count only
            kpis.append(
                {
                    "label": "Models",
                    "value": len(registered_models),
                    "icon": "layers",
                    "change": None,
                }
            )

        # Chart data (sample data if no database)
        activity_labels = []
        activity_values = []

        # Last 7 days
        for i in range(6, -1, -1):
            date = datetime.now() - timedelta(days=i)
            activity_labels.append(date.strftime("%a"))
            # Sample data (in production, query actual activity)
            activity_values.append(max(0, 10 - i * 2 + (i % 3)))

        # Model distribution data
        model_labels = list(model_counts.keys())[:5]  # Top 5 models
        model_values = [model_counts.get(name, 0) for name in model_labels]

        # If no data, use sample
        if not model_values or sum(model_values) == 0:
            model_labels = registered_models[:5]
            model_values = [5, 3, 2, 1, 1]

        chart_data = {
            "activity_labels": activity_labels,
            "activity_values": activity_values,
            "model_labels": model_labels,
            "model_values": model_values,
        }

        # Recent activity (if audit logging enabled)
        recent_activity = []
        # TODO: Query audit log if available

        context = {
            **get_common_context(request),
            "kpis": kpis,
            "registered_models": registered_models,
            "chart_data": chart_data,
            "recent_activity": recent_activity,
        }

        return templates.TemplateResponse("pages/index.html", context)

    # ==================== List View ====================

    @router.get("/{model}/", response_class=HTMLResponse, name="admin:list")
    async def list_view(
        request: Request,
        model: str,
        page: int = Query(1, ge=1),
        per_page: int = Query(25, ge=1, le=100),
        search: str | None = Query(None),
        session: "AsyncSession" = Depends(session_dependency)
        if session_dependency
        else None,
    ):
        """List all records of a model."""
        # Validate model access
        try:
            model_config = registry.validate_model_access(model)
        except Exception:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="Model not registered"
            )

        # Get field definitions for column headers
        # For SQLAlchemy models, skip schema walking (use list_display directly)
        if hasattr(model_config.model, "__tablename__"):
            # SQLAlchemy model - use list_display directly
            display_fields = model_config.list_display or ["id"]
        else:
            # Pydantic model - use schema walker
            fields = walker.walk(model_config.model)
            display_fields = model_config.list_display or [f.name for f in fields[:5]]

        columns = [
            {"field": name, "label": name.replace("_", " ").title(), "sortable": True}
            for name in display_fields
        ]

        # Fetch data from database if session available
        if session and hasattr(model_config.model, "__tablename__"):
            # SQLAlchemy model - use CRUD
            crud = CRUDBase(model_config.model)

            rows_data, total = await crud.list(
                session,
                page=page,
                per_page=per_page,
                search=search,
                search_fields=model_config.searchable_fields,
                order_by=model_config.ordering,
            )

            # Convert SQLAlchemy models to dicts for template
            rows = [
                {field: getattr(row, field, None) for field in display_fields + ["id"]}
                for row in rows_data
            ]
            total_pages = math.ceil(total / per_page) if total > 0 else 1
        else:
            # No database or Pydantic-only model
            rows = []
            total_pages = 1

        # Generate signed URLs for actions
        edit_url_template = str(request.url_for("admin:edit", model=model, id="{id}"))
        delete_token = signer.create_fragment_token(model, action="delete")
        delete_url_template = f"{prefix}/{model}/{{id}}/delete?token={delete_token}"

        context = {
            **get_common_context(request),
            "model_config": model_config,
            "current_model": model,
            "columns": columns,
            "rows": rows,
            "page": page,
            "total_pages": total_pages,
            "search_query": search,
            "id_field": "id",
            "edit_url_template": edit_url_template,
            "delete_url_template": delete_url_template,
        }

        return templates.TemplateResponse("pages/list.html", context)

    # ==================== Create View ====================

    @router.get("/{model}/create", response_class=HTMLResponse, name="admin:create")
    async def create_view(request: Request, model: str):
        """Show create form for a model."""
        try:
            model_config = registry.validate_model_access(model)
        except Exception:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="Model not registered"
            )

        if model_config.readonly:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="Model is read-only"
            )

        # Get form fields
        fields = walker.walk(
            model_config.model,
            exclude=model_config.exclude,
            include=model_config.fields if model_config.fields else None,
        )

        # Generate signed fragment URL for polymorphic forms
        fragment_token = signer.create_fragment_token(model, action="load_fragment")
        fragment_url = f"{prefix}/fragments?token={fragment_token}"

        context = {
            **get_common_context(request),
            "model_config": model_config,
            "current_model": model,
            "fields": fields,
            "values": {},
            "errors": {},
            "record_id": None,
            "fragment_url": fragment_url,
            "csrf_token": signer.sign({"action": "create", "model": model}),
        }

        return templates.TemplateResponse("pages/edit.html", context)

    @router.post(
        "/{model}/create", response_class=HTMLResponse, name="admin:create_submit"
    )
    async def create_submit(
        request: Request,
        model: str,
        session: "AsyncSession" = Depends(session_dependency)
        if session_dependency
        else None,
    ):
        """Handle create form submission."""
        try:
            model_config = registry.validate_model_access(model)
        except Exception:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="Model not registered"
            )

        if model_config.readonly:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="Model is read-only"
            )

        form_data = await request.form()

        # Validate CSRF token
        csrf_token = form_data.get("_csrf_token", "")
        try:
            signer.unsign(csrf_token)
        except Exception:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="Invalid CSRF token"
            )

        # Create record in database if session available
        if session and hasattr(model_config.model, "__tablename__"):
            crud = CRUDBase(model_config.model)

            # Convert form data to dict (excluding internal fields)
            create_data = {
                k: v for k, v in dict(form_data).items() if not k.startswith("_")
            }

            try:
                await crud.create(session, obj_in=create_data)
                await session.commit()
            except Exception as e:
                await session.rollback()
                # TODO: Return to form with error message
                raise HTTPException(status_code=400, detail=str(e))

        return RedirectResponse(
            url=str(request.url_for("admin:list", model=model)),
            status_code=303,
        )

    # ==================== Edit View ====================

    @router.get("/{model}/{id}", response_class=HTMLResponse, name="admin:edit")
    async def edit_view(
        request: Request,
        model: str,
        id: str,
        session: "AsyncSession" = Depends(session_dependency)
        if session_dependency
        else None,
    ):
        """Show edit form for a record."""
        try:
            model_config = registry.validate_model_access(model)
        except Exception:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="Model not registered"
            )

        # Get form fields
        fields = walker.walk(
            model_config.model,
            exclude=model_config.exclude,
            include=model_config.fields if model_config.fields else None,
        )

        # Fetch actual record data from database
        values = {"id": id}
        if session and hasattr(model_config.model, "__tablename__"):
            crud = CRUDBase(model_config.model)
            record = await crud.get(session, id)

            if not record:
                raise HTTPException(
                    status_code=HTTP_404_NOT_FOUND, detail="Record not found"
                )

            # Convert to dict for template
            values = {field.name: getattr(record, field.name, None) for field in fields}
            values["id"] = id

        # Generate signed fragment URL
        fragment_token = signer.create_fragment_token(
            model, action="load_fragment", record_id=id
        )
        fragment_url = f"{prefix}/fragments?token={fragment_token}"

        context = {
            **get_common_context(request),
            "model_config": model_config,
            "current_model": model,
            "fields": fields,
            "values": values,
            "errors": {},
            "record_id": id,
            "fragment_url": fragment_url,
            "csrf_token": signer.sign({"action": "update", "model": model, "id": id}),
        }

        return templates.TemplateResponse("pages/edit.html", context)

    @router.post("/{model}/{id}", name="admin:update")
    async def update_submit(
        request: Request,
        model: str,
        id: str,
        session: "AsyncSession" = Depends(session_dependency)
        if session_dependency
        else None,
    ):
        """Handle update form submission."""
        try:
            model_config = registry.validate_model_access(model)
        except Exception:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="Model not registered"
            )

        if model_config.readonly:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="Model is read-only"
            )

        form_data = await request.form()

        # Validate CSRF token
        csrf_token = form_data.get("_csrf_token", "")
        try:
            signer.unsign(csrf_token)
        except Exception:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="Invalid CSRF token"
            )

        # Update record in database
        if session and hasattr(model_config.model, "__tablename__"):
            crud = CRUDBase(model_config.model)

            # Convert form data to dict (excluding internal fields)
            update_data = {
                k: v for k, v in dict(form_data).items() if not k.startswith("_")
            }

            try:
                updated_record = await crud.update(session, id=id, obj_in=update_data)
                if not updated_record:
                    raise HTTPException(
                        status_code=HTTP_404_NOT_FOUND, detail="Record not found"
                    )
                await session.commit()
            except HTTPException:
                raise
            except Exception as e:
                await session.rollback()
                raise HTTPException(status_code=400, detail=str(e))

        return RedirectResponse(
            url=str(request.url_for("admin:list", model=model)),
            status_code=303,
        )

    # ==================== Delete ====================

    @router.delete("/{model}/{id}", name="admin:delete")
    async def delete_record(
        request: Request,
        model: str,
        id: str,
        token: str = Query(...),
        session: "AsyncSession" = Depends(session_dependency)
        if session_dependency
        else None,
    ):
        """Delete a record."""
        # Validate signed token
        try:
            payload = signer.unsign(token)
            if payload.get("model") != model or payload.get("action") != "delete":
                raise ValueError("Token mismatch")
        except Exception:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="Invalid or expired token"
            )

        try:
            model_config = registry.validate_model_access(model)
        except Exception:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="Model not registered"
            )

        if model_config.readonly:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="Model is read-only"
            )

        # Delete record from database
        if session and hasattr(model_config.model, "__tablename__"):
            crud = CRUDBase(model_config.model)

            try:
                deleted = await crud.delete(session, id=id)
                if not deleted:
                    raise HTTPException(
                        status_code=HTTP_404_NOT_FOUND, detail="Record not found"
                    )
                await session.commit()
            except HTTPException:
                raise
            except Exception as e:
                await session.rollback()
                raise HTTPException(status_code=400, detail=str(e))

        # Return empty response for HTMX to remove the row
        return HTMLResponse(content="", status_code=200)

    # ==================== Polymorphic Fragment Loading ====================

    @router.get("/fragments", response_class=HTMLResponse, name="admin:load_fragment")
    async def load_fragment(
        request: Request,
        token: str = Query(...),
        subtype: str = Query(None),
    ):
        """
        Load form fields for a polymorphic subtype.

        This endpoint is called via HTMX when the user selects a different
        type in a discriminated union dropdown. It uses signed tokens to
        prevent IDOR attacks.
        """
        # Validate the signed token
        try:
            payload = signer.unsign(token)
        except Exception as e:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail=f"Invalid or expired token: {e}",
            )

        # Extract and validate model
        model_name = payload.get("model")
        if not model_name:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="Missing model in token"
            )

        try:
            model_config = registry.validate_model_access(model_name)
        except Exception:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="Model not registered"
            )

        # Get subtype from query or form
        if not subtype:
            form_data = await request.form()
            # Get from discriminator field value in the request
            for key, value in form_data.items():
                if value and key not in ["_model", "_csrf_token"]:
                    subtype = value
                    break

        if not subtype:
            return HTMLResponse(
                content="<p class='text-muted-foreground text-sm'>Select a type above</p>"
            )

        # Validate subtype access (Anti-Type-Confusion)
        try:
            subtype_class = registry.validate_subtype_access(model_name, subtype)
        except Exception:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail=f"Subtype '{subtype}' is not allowed for model '{model_name}'",
            )

        # Walk the subtype to get its fields
        # Find the discriminator field name
        discriminator = None
        parent_fields = walker.walk(model_config.model)
        for field in parent_fields:
            if field.discriminator:
                discriminator = field.discriminator
                break

        fields = walker.walk_subtype(subtype_class, parent_discriminator=discriminator)

        context = {
            "request": request,
            "fields": fields,
            "values": {},
            "errors": {},
            "model_name": model_name,
            "csp_nonce": getattr(request.state, "csp_nonce", ""),
        }

        return templates.TemplateResponse("fragments/form_fields.html", context)

    return router
