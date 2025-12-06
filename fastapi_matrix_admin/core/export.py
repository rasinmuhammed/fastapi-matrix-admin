"""
CSV/Excel Export functionality for FastAPI Shadcn Admin.

Provides utilities to export model data to CSV and Excel formats.
"""

from __future__ import annotations

import csv
import io
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

__all__ = ["CSVExporter", "export_to_csv"]


class CSVExporter:
    """
    CSV export utility for model data.

    Features:
    - Exports query results to CSV format
    - Handles pagination
    - Configurable field selection
    - Proper encoding (UTF-8 BOM for Excel compatibility)

    Usage:
        exporter = CSVExporter()
        csv_content = await exporter.export(session, User, fields=["id", "email"])
    """

    def __init__(self, encoding: str = "utf-8-sig"):
        """
        Initialize CSV exporter.

        Args:
            encoding: Character encoding (utf-8-sig adds BOM for Excel)
        """
        self.encoding = encoding

    async def export(
        self,
        session: "AsyncSession",
        model: type,
        fields: list[str] | None = None,
        filters: dict[str, Any] | None = None,
        max_rows: int = 10000,
    ) -> bytes:
        """
        Export model data to CSV.

        Args:
            session: Database session
            model: SQLAlchemy model to export
            fields: Fields to include (None = all)
            filters: Optional filters to apply
            max_rows: Maximum rows to export (safety limit)

        Returns:
            CSV content as bytes
        """
        from sqlalchemy import select

        # Build query
        query = select(model)
        if filters:
            for key, value in filters.items():
                query = query.where(getattr(model, key) == value)

        # Limit for safety
        query = query.limit(max_rows)

        # Execute
        result = await session.execute(query)
        rows = result.scalars().all()

        # Determine fields
        if fields is None:
            # Get all column names
            fields = [c.name for c in model.__table__.columns]

        # Generate CSV
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()

        for row in rows:
            row_dict = {field: getattr(row, field, None) for field in fields}
            writer.writerow(row_dict)

        # Return as bytes
        return output.getvalue().encode(self.encoding)


async def export_to_csv(
    session: "AsyncSession",
    model: type,
    fields: list[str] | None = None,
    **kwargs,
) -> bytes:
    """
    Convenience function to export model to CSV.

    Args:
        session: Database session
        model: Model to export
        fields: Fields to include
        **kwargs: Additional arguments for CSVExporter.export

    Returns:
        CSV content as bytes
    """
    exporter = CSVExporter()
    return await exporter.export(session, model, fields=fields, **kwargs)
