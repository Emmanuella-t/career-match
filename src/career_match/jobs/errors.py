"""Job provider errors for discovery."""

from __future__ import annotations


class JobProviderNotConfiguredError(Exception):
    """Raised when an external job provider is required but not configured."""


class JobProviderError(Exception):
    """Raised when an external job provider request fails."""
