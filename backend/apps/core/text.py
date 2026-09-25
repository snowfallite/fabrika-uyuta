"""Text cleanup for form input (tech.md, 12.1)."""

import unicodedata

# Control and lone surrogate characters: invisible, and Postgres cannot store NUL.
_REMOVED_CATEGORIES = frozenset({"Cc", "Cs"})


def _drop_controls(value: str, keep: str = "") -> str:
    return "".join(
        ch for ch in value if ch in keep or unicodedata.category(ch) not in _REMOVED_CATEGORIES
    )


def clean_name(value: str) -> str:
    """Trim, collapse any whitespace run into one space, drop control characters."""
    return " ".join(_drop_controls(value).split())


def clean_text(value: str) -> str:
    """Trim and drop control characters except newline and tab."""
    return _drop_controls(value, keep="\n\t").strip()
