import json
from pathlib import Path

from app.template.template_model import TemplateModel

TEMPLATE_DIR = Path(__file__).parent.parent.parent / "templates"
TEMPLATE_DIR.mkdir(exist_ok=True)


class TemplateManager:
    """템플릿 파일 CRUD"""

    @staticmethod
    def save(model: TemplateModel, path: Path | None = None) -> Path:
        if path is None:
            safe_name = model.name.replace(" ", "_").replace("/", "_")
            path = TEMPLATE_DIR / f"{safe_name}.json"
        path.write_text(json.dumps(model.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    @staticmethod
    def load(path: Path) -> TemplateModel:
        data = json.loads(path.read_text(encoding="utf-8"))
        return TemplateModel.from_dict(data)

    @staticmethod
    def list_templates() -> list[Path]:
        return sorted(TEMPLATE_DIR.glob("*.json"))

    @staticmethod
    def delete(path: Path):
        if path.exists():
            path.unlink()

    @staticmethod
    def snapshot_from_scene(scene, name: str) -> TemplateModel:
        """현재 캔버스 씬 → TemplateModel 변환"""
        from app.canvas.image_item import ImageItem
        from app.canvas.text_item import TextItem
        from app.canvas.frame_item import FrameItem
        from app.template.template_model import ImageSlot, TextSlot, FrameSlot

        w, h = scene.get_canvas_size()
        model = TemplateModel(
            name=name,
            canvas_w=w,
            canvas_h=h,
            bg_color=scene._bg_color.name(),
        )
        for item in scene.get_layer_items():
            if not hasattr(item, "to_dict"):
                continue
            d = item.to_dict()
            if isinstance(item, ImageItem):
                model.image_slots.append(ImageSlot(
                    slot_id=d["slot_id"] or f"img_{len(model.image_slots)}",
                    x=d["x"], y=d["y"],
                    width=d["width"], height=d["height"],
                    z=d["z"],
                ))
            elif isinstance(item, TextItem):
                model.text_slots.append(TextSlot(
                    slot_id=d["slot_id"] or f"txt_{len(model.text_slots)}",
                    x=d["x"], y=d["y"],
                    content=d["content"],
                    font_family=d["font_family"],
                    font_size=d["font_size"],
                    bold=d["bold"],
                    italic=d["italic"],
                    color=d["color"],
                    stroke_width=d.get("stroke_width", 0.0),
                    stroke_color=d.get("stroke_color", "#000000"),
                    text_width=d.get("text_width", 400),
                    z=d["z"],
                ))
            elif isinstance(item, FrameItem):
                model.frame_slots.append(FrameSlot(
                    frame_id=d["frame_id"] or f"frame_{len(model.frame_slots)}",
                    x=d["x"], y=d["y"],
                    width=d["width"], height=d["height"],
                    border_color=d["border_color"],
                    border_width=d["border_width"],
                    z=d["z"],
                ))
        return model

    @staticmethod
    def apply_to_scene(model: TemplateModel, scene):
        """TemplateModel → 캔버스 씬 복원"""
        from PyQt6.QtCore import QPointF
        from PyQt6.QtGui import QPixmap, QColor

        scene.clear_canvas()
        scene.set_canvas_size(model.canvas_w, model.canvas_h)
        scene.set_bg_color(QColor(model.bg_color))

        for slot in sorted(model.image_slots, key=lambda s: s.z):
            placeholder = _make_placeholder_pixmap(int(slot.width), int(slot.height))
            item = scene.add_image(
                placeholder,
                QPointF(slot.x, slot.y),
                slot.width, slot.height,
                slot.slot_id,
            )
            item.setZValue(slot.z)

        for slot in sorted(model.text_slots, key=lambda s: s.z):
            item = scene.add_text(slot.content, QPointF(slot.x, slot.y), slot.slot_id)
            item.set_font_family(slot.font_family)
            item.set_font_size(slot.font_size)
            item.set_bold(slot.bold)
            item.set_italic(slot.italic)
            from PyQt6.QtGui import QColor as QC
            item.set_color(QC(slot.color))
            item.set_stroke(slot.stroke_width, QC(slot.stroke_color))
            if slot.text_width > 0:
                item.setTextWidth(slot.text_width)
            item.setZValue(slot.z)

        for slot in sorted(model.frame_slots, key=lambda s: s.z):
            item = scene.add_frame(
                slot.x, slot.y, slot.width, slot.height,
                slot.frame_id, slot.border_color, slot.border_width,
            )
            item.setZValue(slot.z)


def _make_placeholder_pixmap(w: int, h: int):
    from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen, QFont
    from PyQt6.QtCore import Qt, QRectF
    pm = QPixmap(max(w, 1), max(h, 1))
    pm.fill(QColor("#e5e7eb"))
    painter = QPainter(pm)
    pen = QPen(QColor("#9ca3af"), 2, Qt.PenStyle.DashLine)
    painter.setPen(pen)
    painter.drawRect(2, 2, w - 4, h - 4)
    painter.drawLine(0, 0, w, h)
    painter.drawLine(w, 0, 0, h)
    painter.setFont(QFont("sans-serif", max(10, min(h // 8, 20))))
    painter.setPen(QColor("#6b7280"))
    painter.drawText(QRectF(0, 0, w, h), Qt.AlignmentFlag.AlignCenter, "이미지 영역")
    painter.end()
    return pm
