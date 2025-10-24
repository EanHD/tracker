"""Shared console utilities with accessibility awareness."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional

from rich.console import Console


@dataclass
class AccessibilityOptions:
    """Accessibility options propagated across the CLI."""

    plain_mode: bool = False
    no_color: bool = False
    no_emoji: bool = False


_accessibility = AccessibilityOptions()
_console = Console()


def _env_flag(name: str) -> bool:
    """Interpret environment variable as boolean."""
    value = os.getenv(name)
    if value is None:
        return False
    value = value.strip().lower()
    return value in {"1", "true", "yes", "on"}


def configure_accessibility(
    *,
    plain: bool = False,
    no_color: bool = False,
    no_emoji: bool = False,
) -> None:
    """Configure console behaviour based on CLI flags or environment."""
    global _console

    env_plain = _env_flag("TRACKER_PLAIN_MODE")
    env_no_color = _env_flag("TRACKER_NO_COLOR")
    env_no_emoji = _env_flag("TRACKER_NO_EMOJI")

    _accessibility.plain_mode = plain or env_plain
    _accessibility.no_color = _accessibility.plain_mode or no_color or env_no_color
    _accessibility.no_emoji = _accessibility.plain_mode or no_emoji or env_no_emoji

    _console = Console(
        no_color=_accessibility.no_color,
        emoji=not _accessibility.no_emoji,
        highlight=not _accessibility.plain_mode,
        markup=True,
    )

    # Clear cached helpers that depend on accessibility state.
    icon.cache_clear()


def get_console() -> Console:
    """Return the shared console instance."""
    return _console


def accessibility() -> AccessibilityOptions:
    """Expose current accessibility configuration."""
    return _accessibility


@lru_cache(maxsize=None)
def icon(default: str, fallback: str) -> str:
    """Return icon respecting emoji preference."""
    return fallback if _accessibility.no_emoji else default


def emphasize(text: str, descriptor: Optional[str] = None) -> str:
    """
    Append descriptor in plain mode so styling intent is still communicated.
    """
    if not _accessibility.plain_mode or not descriptor:
        return text
    return f"{text} ({descriptor})"


def qualitative_scale(value: int, *, low: range, medium: range, high: range) -> str:
    """Return qualitative description for numeric scales."""
    if value in low:
        return "low"
    if value in medium:
        return "moderate"
    if value in high:
        return "high"
    return "unknown"
