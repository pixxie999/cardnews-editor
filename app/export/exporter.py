import io
from pathlib import Path

from PyQt6.QtGui import QImage
from PyQt6.QtCore import QBuffer, QByteArray
from PIL import Image


def export_image(qimage: QImage, output_path: str | Path, quality: int = 95):
    """QImage → Pillow → 파일 저장 (jpg/png/webp 지원)"""
    output_path = Path(output_path)
    fmt = output_path.suffix.lstrip(".").upper()
    if fmt == "JPG":
        fmt = "JPEG"

    buf = QBuffer()
    buf.open(QBuffer.OpenModeFlag.ReadWrite)
    qimage.save(buf, "PNG")
    buf.seek(0)
    pil_img = Image.open(io.BytesIO(bytes(buf.data())))

    if fmt == "JPEG":
        pil_img = pil_img.convert("RGB")

    save_kwargs: dict = {}
    if fmt in ("JPEG", "WEBP"):
        save_kwargs["quality"] = quality
    if fmt == "WEBP":
        save_kwargs["method"] = 6

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pil_img.save(str(output_path), format=fmt, **save_kwargs)
