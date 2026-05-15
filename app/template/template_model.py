from dataclasses import dataclass, field
from typing import Any


@dataclass
class TextSlot:
    slot_id: str
    x: float = 50
    y: float = 50
    content: str = "텍스트를 입력하세요"
    font_family: str = "맑은 고딕"
    font_size: int = 24
    bold: bool = False
    italic: bool = False
    color: str = "#222222"
    z: float = 1


@dataclass
class ImageSlot:
    slot_id: str
    x: float = 0
    y: float = 0
    width: float = 400
    height: float = 300
    z: float = 0
    source: str = ""  # 배치 처리 시 채워짐


@dataclass
class TemplateModel:
    name: str = "새 템플릿"
    canvas_w: int = 1080
    canvas_h: int = 1080
    bg_color: str = "#ffffff"
    image_slots: list[ImageSlot] = field(default_factory=list)
    text_slots: list[TextSlot] = field(default_factory=list)

    # ------------------------------------------------------------------
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "canvas_w": self.canvas_w,
            "canvas_h": self.canvas_h,
            "bg_color": self.bg_color,
            "image_slots": [vars(s) for s in self.image_slots],
            "text_slots": [vars(s) for s in self.text_slots],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TemplateModel":
        m = cls(
            name=data.get("name", "템플릿"),
            canvas_w=data.get("canvas_w", 1080),
            canvas_h=data.get("canvas_h", 1080),
            bg_color=data.get("bg_color", "#ffffff"),
        )
        for s in data.get("image_slots", []):
            m.image_slots.append(ImageSlot(**s))
        for s in data.get("text_slots", []):
            m.text_slots.append(TextSlot(**s))
        return m
