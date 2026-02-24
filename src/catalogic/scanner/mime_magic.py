"""MIME-тип через python-magic (libmagic)."""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import magic

_MAGIC: "magic.Magic | None" = None


def _get_magic() -> "magic.Magic | None":
    global _MAGIC
    if _MAGIC is None:
        try:
            import magic

            _MAGIC = magic.Magic(mime=True)
        except Exception:
            pass
    return _MAGIC


def get_mime(path: Path | str) -> str | None:
    """Определяет MIME по содержимому файла (magic). При недоступности libmagic — fallback по расширению."""
    path = Path(path)
    if not path.is_file():
        return None
    m = _get_magic()
    if m is not None:
        try:
            return m.from_file(str(path))
        except Exception:
            pass
    import mimetypes
    guess, _ = mimetypes.guess_type(path.name, strict=False)
    return guess
