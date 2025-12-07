"""
Admin Router for FastAPI Shadcn Admin.

Implements all admin endpoints with security validation:
- Dashboard and list views
- Create, edit, delete operations
- Signed fragment loading for polymorphic forms
"""

from __future__ import annotations

import math
import platform
import psutil
from datetime import datetime, timedelta
from typing import Any, TYPE_CHECKING, Callable, AsyncGenerator

from fastapi import APIRouter, Request, HTTPException, Depends, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

if TYPE_CHECKING:
    from fastapi_matrix_admin.core.registry import AdminRegistry
    from fastapi_matrix_admin.core.security import URLSigner
    from fastapi_matrix_admin.core.integrator import SchemaWalker
    from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_matrix_admin.core.crud import CRUDBase
from fastapi_matrix_admin.core.integrator import FieldDefinition, FieldType
from fastapi_matrix_admin.audit.models import AuditLogger
from fastapi_matrix_admin.core.rate_limiter import RateLimiter


def extract_sqlalchemy_fields(
    model: Any, exclude: list[str] | None = None, include: list[str] | None = None
) -> list[FieldDefinition]:
    """
    Extract fields from a SQLAlchemy model and convert to FieldDefinition objects.

    Args:
        model: SQLAlchemy model class
        exclude: List of field names to exclude
        include: List of field names to include (if specified, only these fields are included)

    Returns:
        List of FieldDefinition objects for template rendering
    """
    from sqlalchemy import inspect as sqla_inspect
    from sqlalchemy.orm import ColumnProperty

    mapper = sqla_inspect(model)
    fields = []

    # Get all columns
    for attr in mapper.attrs:
        if isinstance(attr, ColumnProperty):
            column = attr.columns[0]
            field_name = attr.key

            # Apply include/exclude filters
            if include and field_name not in include:
                continue
            if exclude and field_name in exclude:
                continue

            # Skip primary key (id) - it's auto-generated
            if column.primary_key:
                continue

            # Determine field type from SQLAlchemy column type
            field_type = FieldType.TEXT  # Default
            python_type = column.type.python_type
            target_model = None

            # Check for Foreign Keys
            if column.foreign_keys:
                field_type = FieldType.RELATIONSHIP
                # Get target table name
                fk = list(column.foreign_keys)[0]
                # Try to map table name back to model name if possible, or just use table name
                # Optimally, we want the Model Name (e.g. "User") for the API search
                # We can store the table name and let the registry lookup handle it later?
                # Or simplistic approach: Use the table name.
                target_table = fk.column.table.name
                # TODO: We need a way to map table_name -> Registry Model Name
                # For now, let's assume table name or look up via registry reverse lookup in future.
                target_model = target_table
            elif python_type is bool:
                field_type = FieldType.BOOLEAN
            elif python_type is int:
                field_type = FieldType.NUMBER
            elif python_type is float:
                field_type = FieldType.FLOAT
            elif hasattr(column.type, "__visit_name__"):
                if column.type.__visit_name__ == "text":
                    field_type = FieldType.TEXTAREA
                elif column.type.__visit_name__ in ("date", "datetime"):
                    field_type = FieldType.DATETIME

            # Create FieldDefinition
            field_def = FieldDefinition(
                name=field_name,
                field_type=field_type,
                required=not column.nullable,
                default=(
                    column.default.arg
                    if column.default and hasattr(column.default, "arg")
                    else None
                ),
                title=field_name.replace("_", " ").title(),
                description=None,
                placeholder=None,
                target_model=target_model,
            )

            fields.append(field_def)

    return fields


def create_admin_router(
    registry: "AdminRegistry",
    signer: "URLSigner",
    walker: "SchemaWalker",
    templates,
    prefix: str = "/admin",
    title: str = "Admin",
    session_dependency: (
        Callable[[], AsyncGenerator["AsyncSession", None]] | None
    ) = None,
    audit_logger: AuditLogger | None = None,
    auth_model: Any | None = None,
    demo_mode: bool = False,
) -> APIRouter:
    # Initialize rate limiter (e.g., 5 login attempts per minute)
    login_limiter = RateLimiter(rate=5, per=60)
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

    # ==================== Auth ====================

    @router.get("/login", response_class=HTMLResponse, name="admin:login")
    async def login_view(request: Request):
        """Show login form."""
        context = {
            "request": request,
            "title": title,
            "prefix": prefix,
            "csp_nonce": getattr(request.state, "csp_nonce", ""),
            "error": request.query_params.get("error"),
            "demo_mode": demo_mode,
        }
        return templates.TemplateResponse("pages/login.html", context)

    @router.post("/login", response_class=HTMLResponse, name="admin:login_submit")
    async def login_submit(
        request: Request,
        session: "AsyncSession" = (
            Depends(session_dependency) if session_dependency else None
        ),
    ):
        """Handle login submission with rate limiting and security."""
        # 1. IP-based Rate Limiting
        client_ip = request.client.host if request.client else "unknown"
        if not login_limiter.consume(client_ip):
            # Slow down response to prevent timing attacks
            import asyncio

            await asyncio.sleep(1.0)
            
            context = {
                "request": request,
                "title": title,
                "prefix": prefix,
                "csp_nonce": getattr(request.state, "csp_nonce", ""),
                "error": "Too many login attempts. Please try again later.",
            }
            return templates.TemplateResponse(
                "pages/login.html", context, status_code=429
            )

        form_data = await request.form()
        username = form_data.get("username")
        password = form_data.get("password")

        user = None
        valid_password = False

        # 2. Database Lookup & Auth Logic
        if session and auth_model:
             # Bulletproof DB Auth
             from sqlalchemy import select
             stmt = select(auth_model).where(auth_model.username == username)
             result = await session.execute(stmt)
             user = result.scalar_one_or_none()
             
             if user and hasattr(user, "verify_password"):
                 valid_password = user.verify_password(password)
        
        # If no user found via DB lookups then fails.
        if not user or not valid_password:
            # Add a small delay for failed attempts
            import asyncio
            await asyncio.sleep(0.5)
            
            return templates.TemplateResponse(
                "pages/login.html",
                {
                    "request": request,
                    "title": title,
                    "prefix": prefix,
                    "csp_nonce": getattr(request.state, "csp_nonce", ""),
                    "error": "Invalid credentials",
                },
                status_code=401,
            )

        if hasattr(user, "is_active") and not user.is_active:
            return templates.TemplateResponse(
                "pages/login.html",
                {
                    "request": request,
                    "admin_title": title,
                    "csp_nonce": getattr(request.state, "csp_nonce", ""),
                    "error": "Account disabled",
                },
                status_code=403,
            )

        # 4. Session Creation
        from fastapi_matrix_admin.auth.models import SessionData

        session_data = SessionData.create(
            user, remember_me=bool(form_data.get("remember_me"))
        )

        # Serialize session (using signer for tamper-proof cookie)
        session_token = signer.sign(session_data.model_dump())

        # 5. Success - Set Cookie & Redirect
        response = RedirectResponse(url=f"{prefix}/", status_code=303)
        response.set_cookie(
            key="admin_session",
            value=session_token,
            httponly=True,
            samesite="lax",
            secure=True,  # Require HTTPS (Matrix Admin standard)
            max_age=3600 * 24 * 30 if session_data.expires_at else 3600 * 24,
        )

        # Audit Log Login
        if audit_logger:
            # We don't await this to keep login fast? No, await for reliability.
            # Using fire-and-forget might be better for perf but safety first.
            await audit_logger.log_create(
                session,
                "Auth",
                "login",
                {"username": username},
                user_id=user.id,
                ip_address=client_ip,
            )

        return response

    @router.get("/logout", name="admin:logout")
    async def logout(request: Request):
        response = RedirectResponse(url=f"{prefix}/login", status_code=303)
        response.delete_cookie("admin_session")
        return response

    # ==================== Dashboard ====================

    @router.get("/", response_class=HTMLResponse, name="admin:index")
    async def dashboard(
        request: Request,
        session: "AsyncSession" = (
            Depends(session_dependency) if session_dependency else None
        ),
    ):
        """Admin dashboard with analytics."""
        from datetime import datetime
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

        # System KPIs (Observer Module)
        system_stats = {
            "platform": f"{platform.system()} {platform.release()}",
            "processor": platform.processor(),
            "cpu_usage": psutil.cpu_percent(interval=None),
            "ram_usage": psutil.virtual_memory().percent,
            "ram_total": f"{round(psutil.virtual_memory().total / (1024**3), 2)} GB",
            "disk_usage": psutil.disk_usage("/").percent,
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        }

        # Add System Stats to KPIs
        kpis.append(
            {
                "label": "CPU Load",
                "value": f"{system_stats['cpu_usage']}%",
                "icon": "cpu",
                "change": None,
            }
        )
        kpis.append(
            {
                "label": "RAM Usage",
                "value": f"{system_stats['ram_usage']}%",
                "icon": "activity",
                "change": None,
            }
        )

        context = {
            **get_common_context(request),
            "kpis": kpis,
            "registered_models": registered_models,
            "chart_data": chart_data,
            "recent_activity": recent_activity,
            "system_stats": system_stats,  # Pass full stats if needed
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
        session: "AsyncSession" = (
            Depends(session_dependency) if session_dependency else None
        ),
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

        # Prepare Filter Definitions
        # We need to know the type of each filter field to render the correct widget
        filter_definitions = []
        if model_config.filter_fields:
            # Create a lookup map only for fields in filter_fields
            # If using SQLAlchemy, we might need to be clever.
            # Reuse the extraction logic or walker logic.

            all_fields = []
            if hasattr(model_config.model, "__tablename__"):
                all_fields = extract_sqlalchemy_fields(
                    model_config.model, include=model_config.filter_fields
                )
            else:
                all_fields = walker.walk(
                    model_config.model, include=model_config.filter_fields
                )

            # Re-order to match filter_fields configuration
            field_map = {f.name: f for f in all_fields}
            for name in model_config.filter_fields:
                if name in field_map:
                    filter_definitions.append(field_map[name])

        # Extract filters from query params
        reserved_params = {"page", "per_page", "search"}
        filters = {
            k: v for k, v in request.query_params.items() if k not in reserved_params
        }

        # Fetch data from database if session available
        if session and hasattr(model_config.model, "__tablename__"):
            # SQLAlchemy model - use CRUD
            crud = CRUDBase(model_config.model)
            
            # Optimization: Detect relationships to eager load (N+1 prevention)
            load_relationships = []
            from sqlalchemy import inspect
            inspector = inspect(model_config.model)
            for field in display_fields:
                if field in inspector.relationships:
                    load_relationships.append(field)

            rows_data, total = await crud.list(
                session,
                page=page,
                per_page=per_page,
                search=search,
                search_fields=model_config.searchable_fields,
                filters=filters,
                order_by=model_config.ordering,
                load_relationships=load_relationships,
            )
        else:
            # Pydantic/No-DB model - empty or mock data
            rows_data = []  # TODO: Maybe implement in-memory filter?
            total = 0

        # Context Variables
        edit_url_template = router.url_path_for("admin:edit", model=model, id="__id__")
        delete_url_template = router.url_path_for(
            "admin:delete", model=model, id="__id__"
        )

        context = {
            **get_common_context(request),
            "model": model,
            "model_config": model_config,
            "columns": columns,
            "rows": rows_data,
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": math.ceil(total / per_page) if per_page > 0 else 1,
            "search_query": search,
            "id_field": "id",
            "edit_url_template": edit_url_template,
            "delete_url_template": delete_url_template,
            "active_filters": filters,
            "filter_definitions": filter_definitions,
        }

        return templates.TemplateResponse("pages/list.html", context)

    @router.get("/{model}/export/csv", name="admin:export_csv")
    async def export_csv(
        request: Request,
        model: str,
        search: str | None = Query(None),
        session: "AsyncSession" = (
            Depends(session_dependency) if session_dependency else None
        ),
    ):
        """Export filtered data as CSV."""
        try:
            model_config = registry.validate_model_access(model)
        except Exception:
            raise HTTPException(status_code=403, detail="Model not registered")

        # Reuse filter logic
        reserved_params = {"page", "per_page", "search"}
        filters = {
            k: v for k, v in request.query_params.items() if k not in reserved_params
        }

        # Determine fields to export
        if hasattr(model_config.model, "__tablename__"):
            fields = model_config.list_display or ["id"]  # Fallback
            # If list_display is empty, maybe get all columns?
            if not model_config.list_display:
                from sqlalchemy import inspection

                fields = [c.key for c in inspection.inspect(model_config.model).columns]
        else:
            fields = model_config.list_display
            if not fields:
                fields = [f.name for f in walker.walk(model_config.model)]

        async def generate_csv():
            import csv
            import io

            # Helper for writing valid CSV lines to stream
            def line(data):
                si = io.StringIO()
                cw = csv.writer(si)
                cw.writerow(data)
                return si.getvalue()

            # Yield Header
            yield line([f.replace("_", " ").title() for f in fields])

            if session and hasattr(model_config.model, "__tablename__"):
                crud = CRUDBase(model_config.model)
                page = 1
                while True:
                    # Fetch in chunks of 500
                    rows, _ = await crud.list(
                        session,
                        page=page,
                        per_page=500,
                        search=search,
                        search_fields=model_config.searchable_fields,
                        filters=filters,
                        order_by=model_config.ordering,
                    )

                    if not rows:
                        break

                    for row in rows:
                        yield line([getattr(row, f, "") for f in fields])

                    page += 1
            else:
                # No DB support yet for non-SQLAlchemy export in this MVP
                yield line(["No database session available"])

        from fastapi.responses import StreamingResponse

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"{model_config.name}_export_{timestamp}.csv"

        return StreamingResponse(
            generate_csv(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

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

        # Get form fields - use SQLAlchemy inspector for SQLAlchemy models
        if hasattr(model_config.model, "__tablename__"):
            # SQLAlchemy model
            fields = extract_sqlalchemy_fields(
                model_config.model,
                exclude=model_config.exclude,
                include=model_config.fields,
            )
        else:
            # Pydantic model
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
        session: "AsyncSession" = (
            Depends(session_dependency) if session_dependency else None
        ),
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
            raw_data = {
                k: v for k, v in dict(form_data).items() if not k.startswith("_")
            }

            # Convert string values to appropriate types based on model
            create_data = {}
            fields = extract_sqlalchemy_fields(model_config.model)
            for field in fields:
                if field.name in raw_data:
                    value = raw_data[field.name]
                    # Convert boolean strings to actual booleans
                    if field.field_type == FieldType.BOOLEAN:
                        create_data[field.name] = value in (
                            "true",
                            "True",
                            "1",
                            "on",
                            True,
                        )
                    # Convert numeric strings to numbers
                    elif field.field_type == FieldType.NUMBER and isinstance(
                        value, str
                    ):
                        create_data[field.name] = int(value) if value else None
                    elif field.field_type == FieldType.FLOAT and isinstance(value, str):
                        create_data[field.name] = float(value) if value else None
                    else:
                        create_data[field.name] = value if value != "" else None

            try:
                await crud.create(session, obj_in=create_data)

                # Audit Log
                if audit_logger:
                    # TODO: specific user info if auth integrated
                    await audit_logger.log_create(
                        session,
                        model_name=model,
                        record_id="new",  # Ideally get ID from created obj
                        record_data=create_data,
                        ip_address=request.client.host if request.client else None,
                    )

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
        session: "AsyncSession" = (
            Depends(session_dependency) if session_dependency else None
        ),
    ):
        """Show edit form for a record."""
        try:
            model_config = registry.validate_model_access(model)
        except Exception:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="Model not registered"
            )

        # Get form fields - use SQLAlchemy inspector for SQLAlchemy models
        if hasattr(model_config.model, "__tablename__"):
            # SQLAlchemy model
            fields = extract_sqlalchemy_fields(
                model_config.model,
                exclude=model_config.exclude,
                include=model_config.fields,
            )
        else:
            # Pydantic model
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
        session: "AsyncSession" = (
            Depends(session_dependency) if session_dependency else None
        ),
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
            raw_data = {
                k: v for k, v in dict(form_data).items() if not k.startswith("_")
            }

            # Convert string values to appropriate types based on model
            update_data = {}
            fields = extract_sqlalchemy_fields(model_config.model)
            for field in fields:
                if field.name in raw_data:
                    value = raw_data[field.name]
                    # Convert boolean strings to actual booleans
                    if field.field_type == FieldType.BOOLEAN:
                        update_data[field.name] = value in (
                            "true",
                            "True",
                            "1",
                            "on",
                            True,
                        )
                    # Convert numeric strings to numbers
                    elif field.field_type == FieldType.NUMBER and isinstance(
                        value, str
                    ):
                        update_data[field.name] = int(value) if value else None
                    elif field.field_type == FieldType.FLOAT and isinstance(value, str):
                        update_data[field.name] = float(value) if value else None
                    else:
                        update_data[field.name] = value if value != "" else None

            try:
                updated_record = await crud.update(session, id=id, obj_in=update_data)
                if not updated_record:
                    raise HTTPException(
                        status_code=HTTP_404_NOT_FOUND, detail="Record not found"
                    )

                # Audit Log
                if audit_logger:
                    await audit_logger.log_update(
                        session,
                        model_name=model,
                        record_id=id,
                        old_data={},  # TODO: Fetch old data for diff
                        new_data=update_data,
                        ip_address=request.client.host if request.client else None,
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
        session: "AsyncSession" = (
            Depends(session_dependency) if session_dependency else None
        ),
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

                # Audit Log
                if audit_logger:
                    await audit_logger.log_delete(
                        session,
                        model_name=model,
                        record_id=id,
                        record_data={},
                        ip_address=request.client.host if request.client else None,
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
