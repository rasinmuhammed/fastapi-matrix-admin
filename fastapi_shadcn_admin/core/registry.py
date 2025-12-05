"""
Model Registry for FastAPI Shadcn Admin.

Provides type-safe model registration and validation with support for
polymorphic models (Pydantic discriminated unions).

Architectural Decision:
We use a centralized registry instead of decorators because:
1. Explicit registration makes dependencies clear
2. Allows runtime model discovery (auto_discover)
3. Enables strict validation before route binding
4. Supports both Pydantic and SQLAlchemy models

Security:
Registry acts as a whitelist, preventing unauthorized model access.
This is critical for preventing IDOR and information disclosure.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Type, TYPE_CHECKING

from pydantic import BaseModel


# Public API
__all__ = [
    "ModelConfig",
    "AdminRegistry",
    "ModelNotFoundError",
    "SubtypeNotAllowedError",
]

if TYPE_CHECKING:
    from sqlalchemy.orm import DeclarativeBase


class RegistryError(Exception):
    """Raised when registry operations fail."""

    pass


class ModelNotFoundError(RegistryError):
    """Raised when a model is not found in the registry."""

    pass


class SubtypeNotAllowedError(RegistryError):
    """Raised when attempting to use an unregistered subtype."""

    pass


@dataclass
class ModelConfig:
    """
    Configuration for a registered model.

    Attributes:
        model: The Pydantic model or SQLAlchemy model class
        name: Display name for the model (defaults to class name)
        subtypes: List of allowed subtypes for polymorphic models
        fields: List of field names to include (empty = all)
        exclude: List of field names to exclude
        list_display: Fields to show in list view
        searchable_fields: Fields that can be searched
        ordering: Default ordering fields
        icon: Optional icon name for the sidebar
        readonly: Whether the model is read-only
    """

    model: Type[BaseModel] | Type["DeclarativeBase"]
    name: str = ""
    subtypes: list[Type[BaseModel]] = field(default_factory=list)
    fields: list[str] = field(default_factory=list)
    exclude: list[str] = field(default_factory=list)
    list_display: list[str] = field(default_factory=list)
    searchable_fields: list[str] = field(default_factory=list)
    ordering: list[str] = field(default_factory=list)
    icon: str = "file"
    readonly: bool = False

    # Internal fields
    _subtype_names: set[str] = field(default_factory=set, init=False, repr=False)

    def __post_init__(self):
        """Initialize derived fields."""
        if not self.name:
            self.name = self.model.__name__

        # Build subtype name set for fast lookup
        self._subtype_names = {st.__name__ for st in self.subtypes}

    def is_subtype_allowed(self, subtype_name: str) -> bool:
        """
        Check if a subtype is allowed for this model.

        Args:
            subtype_name: Name of the subtype to check

        Returns:
            True if the subtype is allowed
        """
        # If no subtypes defined, no subtypes are allowed
        if not self.subtypes:
            return False
        return subtype_name in self._subtype_names

    def get_subtype_class(self, subtype_name: str) -> Type[BaseModel]:
        """
        Get the subtype class by name.

        Args:
            subtype_name: Name of the subtype

        Returns:
            The subtype class

        Raises:
            SubtypeNotAllowedError: If subtype is not registered
        """
        for subtype in self.subtypes:
            if subtype.__name__ == subtype_name:
                return subtype
        raise SubtypeNotAllowedError(
            f"Subtype '{subtype_name}' is not registered for model '{self.name}'"
        )


class AdminRegistry:
    """
    Strict model registry that requires explicit registration.

    Unlike auto-discovery systems, this registry forces developers to
    explicitly register each model, preventing accidental exposure of
    sensitive models and enabling fine-grained access control.

    Usage:
        registry = AdminRegistry()
        registry.register(User, list_display=["id", "name", "email"])
        registry.register(Content, subtypes=[TextBlock, ImageBlock])

        # Get a registered model
        config = registry.get("User")

        # Validate subtype access
        if not config.is_subtype_allowed("VideoBlock"):
            raise SecurityError("Subtype not allowed")
    """

    def __init__(self):
        """Initialize an empty registry."""
        self._models: dict[str, ModelConfig] = {}

    def register(
        self,
        model: Type[BaseModel] | Type["DeclarativeBase"],
        *,
        name: str | None = None,
        subtypes: list[Type[BaseModel]] | None = None,
        fields: list[str] | None = None,
        exclude: list[str] | None = None,
        list_display: list[str] | None = None,
        searchable_fields: list[str] | None = None,
        ordering: list[str] | None = None,
        icon: str = "file",
        readonly: bool = False,
    ) -> ModelConfig:
        """
        Register a model with the admin.

        Args:
            model: The Pydantic or SQLAlchemy model class
            name: Display name (defaults to class name)
            subtypes: Allowed subtypes for polymorphic unions
            fields: Fields to include (empty = all)
            exclude: Fields to exclude
            list_display: Fields for list view
            searchable_fields: Searchable fields
            ordering: Default ordering
            icon: Sidebar icon name
            readonly: Make model read-only

        Returns:
            The ModelConfig for chaining

        Raises:
            RegistryError: If model is already registered
        """
        model_name = name or model.__name__

        if model_name in self._models:
            raise RegistryError(f"Model '{model_name}' is already registered")

        config = ModelConfig(
            model=model,
            name=model_name,
            subtypes=subtypes or [],
            fields=fields or [],
            exclude=exclude or [],
            list_display=list_display or [],
            searchable_fields=searchable_fields or [],
            ordering=ordering or [],
            icon=icon,
            readonly=readonly,
        )

        self._models[model_name] = config
        return config

    def get(self, name: str) -> ModelConfig:
        """
        Get a registered model by name.

        Args:
            name: The model name

        Returns:
            The ModelConfig

        Raises:
            ModelNotFoundError: If model is not registered
        """
        if name not in self._models:
            raise ModelNotFoundError(f"Model '{name}' is not registered")
        return self._models[name]

    def get_or_none(self, name: str) -> ModelConfig | None:
        """
        Get a registered model or None if not found.

        Args:
            name: The model name

        Returns:
            The ModelConfig or None
        """
        return self._models.get(name)

    def is_registered(self, name: str) -> bool:
        """
        Check if a model is registered.

        Args:
            name: The model name

        Returns:
            True if registered
        """
        return name in self._models

    def all(self) -> list[ModelConfig]:
        """
        Get all registered models.

        Returns:
            List of all ModelConfigs
        """
        return list(self._models.values())

    def names(self) -> list[str]:
        """
        Get all registered model names.

        Returns:
            List of model names
        """
        return list(self._models.keys())

    def get_all(self) -> list[str]:
        """
        Get all registered model names (sorted).

        Alias for names() with deterministic ordering.

        Returns:
            Sorted list of model names for consistent UI rendering

        Note:
            Sorting ensures:
            - Deterministic ordering in dropdowns
            - Consistent test results
            - Better UX (alphabetical makes finding easier)
        """
        return sorted(self.names())

    def validate_model_access(self, model_name: str) -> ModelConfig:
        """
        Validate that a model is registered and return its config.

        This is the primary security check for request handling.

        Args:
            model_name: The model name to validate

        Returns:
            The ModelConfig if valid

        Raises:
            ModelNotFoundError: If model is not registered
        """
        return self.get(model_name)

    def validate_subtype_access(
        self, model_name: str, subtype_name: str
    ) -> Type[BaseModel]:
        """
        Validate that a subtype is allowed for a model.

        This is the security check for polymorphic form loading.

        Args:
            model_name: The parent model name
            subtype_name: The subtype to validate

        Returns:
            The subtype class if valid

        Raises:
            ModelNotFoundError: If parent model is not registered
            SubtypeNotAllowedError: If subtype is not allowed
        """
        config = self.get(model_name)
        return config.get_subtype_class(subtype_name)

    def __len__(self) -> int:
        """Return the number of registered models."""
        return len(self._models)

    def __contains__(self, name: str) -> bool:
        """Check if a model is registered."""
        return name in self._models

    def __iter__(self):
        """Iterate over registered model configs."""
        return iter(self._models.values())
