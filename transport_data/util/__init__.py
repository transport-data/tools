"""Utilities."""


def uline(text: str, char: str = "=") -> str:
    """Underline `text` with `char`."""
    return f"{text}\n{char * len(text)}"
