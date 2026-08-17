"""Root package error definitions."""

from __future__ import annotations

from collections.abc import Mapping

__all__ = ("ApiClientError",)


class ApiClientError(Exception):
    """Root exception for package-defined API client failures."""

    def __init__(
        self,
        message: str,
        *,
        context: Mapping[str, object] | None = None,
    ) -> None:
        """Initialize an error with a safe message and optional diagnostic context."""
        if not isinstance(message, str):
            msg = "message must be str"
            raise TypeError(msg)
        if context is not None and not isinstance(context, Mapping):
            msg = "context must be a mapping or None"
            raise TypeError(msg)

        super().__init__(message)
        self._context = dict(context) if context is not None else None

    @property
    def context(self) -> Mapping[str, object] | None:
        """Return a shallow copy of the optional diagnostic context."""
        if self._context is None:
            return None
        return dict(self._context)

    def __repr__(self) -> str:
        """Return a compact representation that excludes diagnostic context."""
        return f"{type(self).__name__}({self.args[0]!r})"
