from dataclasses import dataclass, field


@dataclass
class TextSlot:
    slot_id: str
    x: float = 50
    y: float = 50
    content: str = "텍스트를 입력하세요"
    font_family: str = "sans-serif"
    font_size: int = 24
    bold: bool = False
    italic: bool = False
    color: str = "#222222"
    stroke_width: float = 0.0
    stroke_color: str = "#000000"
    text_width: float = 400
    z: float = 1


@dataclass
class ImageSlot:
    slot_id: str
    x: float = 0
    y: float = 0
    width: float = 400
    height: float = 300
    z: float = 0
    source: str = ""


@dataclass
class FrameSlot:
    frame_id: str
    x: float = 0
    y: float = 0
    width: float = 400
    height: float = 300
    border_color: str = "#ffffff"
    border_width: float = 2.0
    z: float = 0
    source: str = ""


@dataclass
class TemplateModel:
    name: str = "새 템플릿"
    canvas_w: int = 1080
    canvas_h: int = 1080
    bg_color: str = "#ffffff"
    image_slots: list[ImageSlot] = field(default_factory=list)
    text_slots: list[TextSlot] = field(default_factory=list)
    frame_slots: list[FrameSlot] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "canvas_w": self.canvas_w,
            "canvas_h": self.canvas_h,
            "bg_color": self.bg_color,
            "image_slots": [vars(s) for s in self.image_slots],
            "text_slots":  [vars(s) for s in self.text_slots],
            "frame_slots": [vars(s) for s in self.frame_slots],
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
            m.image_slots.append(ImageSlot(**{k: v for k, v in s.items()
                                              if k in ImageSlot.__dataclass_fields__}))
        for s in data.get("text_slots", []):
            m.text_slots.append(TextSlot(**{k: v for k, v in s.items()
                                            if k in TextSlot.__dataclass_fields__}))
        for s in data.get("frame_slots", []):
            m.frame_slots.append(FrameSlot(**{k: v for k, v in s.items()
                                              if k in FrameSlot.__dataclass_fields__}))
        return m
