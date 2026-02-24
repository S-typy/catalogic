"""Метаданные изображения: размер в пикселях, DPI, глубина цвета."""

from pathlib import Path

from catalogic.core.entities import ImageMetadata

try:
    from PIL import Image
except ImportError:
    Image = None  # type: ignore[misc, assignment]


def get_image_metadata(path: Path | str) -> ImageMetadata | None:
    """Извлекает размер (px), DPI и глубину цвета. При ошибке или отсутствии Pillow — None."""
    if Image is None:
        return None
    path = Path(path)
    if not path.is_file():
        return None
    try:
        with Image.open(path) as img:
            width, height = img.size
            dpi = img.info.get("dpi")
            if isinstance(dpi, (tuple, list)) and len(dpi) >= 2:
                dpi_x, dpi_y = float(dpi[0]), float(dpi[1])
            else:
                dpi_x = dpi_y = None

            # Глубина цвета: bits per pixel или mode
            color_depth_bits: int | None = None
            if hasattr(img, "bits") and img.bits is not None:
                color_depth_bits = img.bits * len(img.getbands())
            else:
                mode_bits = {"1": 1, "L": 8, "P": 8, "RGB": 24, "RGBA": 32, "CMYK": 32, "I": 32, "F": 32}
                color_depth_bits = mode_bits.get(img.mode)

        return ImageMetadata(
            width_px=width,
            height_px=height,
            dpi_x=dpi_x,
            dpi_y=dpi_y,
            color_depth_bits=color_depth_bits,
        )
    except Exception:
        return None
