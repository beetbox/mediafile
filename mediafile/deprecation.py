import warnings
from importlib import import_module, metadata
from typing import Any

from packaging.version import Version


def _format_message(old: str, new: str) -> str:
    next_major = f"{Version(metadata.version('mediafile')).major + 1}.0.0"
    msg = f"'{old}' is deprecated and will be removed in version '{next_major}'."
    msg += f" Use '{new}' instead."
    return msg


def deprecate_imports(
    old_module: str, new_module_by_name: dict[str, str], name: str
) -> Any:
    """Handle deprecated module imports by redirecting to new locations.

    Facilitates gradual migration of module structure by intercepting import
    attempts for relocated functionality. Issues deprecation warnings while
    transparently providing access to the moved implementation, allowing
    existing code to continue working during transition periods.
    """
    if new_module := new_module_by_name.get(name):
        warnings.warn(
            _format_message(f"{old_module}.{name}", f"{new_module}.{name}"),
            DeprecationWarning,
            stacklevel=2,
        )
        return getattr(import_module(new_module), name)
    raise AttributeError(f"module '{old_module}' has no attribute '{name}'")
