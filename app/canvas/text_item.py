import platform
from PyQt6.QtWidgets import QGraphicsItem, QMenu, QGraphicsRectItem
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import (
    QPen, QColor, QFont, QFontDatabase, QPainter,
    QPainterPath, QTextCursor, QBrush
)
from PyQt6.QtWidgets import QGraphicsTextItem

HANDLE_SIZE = 10


def _default_korean_font() -> str:
    available = set(QFontDatabase.families())
    candidates = {
        "Windows": ["맑은 고딕", "굴림"],
        "Darwin":  ["Apple SD Gothic Neo", "Nanum Gothic", "AppleGothic"],
        "Linux":   ["Noto Sans CJK KR", "Nanum Gothic"],
    }
    for name in candidates.get(platform.system(), []):
        if name in available:
            return name
    return ""


class TextResizeHandle(QGraphicsRectItem):
    def __init__(self, pos_key: str, parent):
        super().__init__(-HANDLE_SIZE / 2, -HANDLE_SIZE / 2, HANDLE_SIZE, HANDLE_SIZE, parent)
        self.pos_key = pos_key
        self.setBrush(QColor("#ffffff"))
        self.setPen(QPen(QColor("#f59e0b"), 1.5))
        self.setZValue(2000)
        cursor_map = {
            'ml': Qt.CursorShape.SizeHorCursor, 'mr': Qt.CursorShape.SizeHorCursor,
            'tl': Qt.CursorShape.SizeFDiagCursor, 'br': Qt.CursorShape.SizeFDiagCursor,
            'tr': Qt.CursorShape.SizeBDiagCursor, 'bl': Qt.CursorShape.SizeBDiagCursor,
        }
        self.setCursor(cursor_map.get(pos_key, Qt.CursorShape.SizeAllCursor))


class TextItem(QGraphicsTextItem):
    """
    더블클릭 편집, 텍스트 스트로크(외곽선), 마우스 리사이즈 지원.
    - 좌/우 핸들: 텍스트 박스 너비 조정 (줄바꿈 조정)
    - 코너 핸들: 폰트 크기 비례 조정
    """

    MIN_WIDTH = 40

    def __init__(self, text: str = "텍스트를 입력하세요", slot_id: str = ""):
        super().__init__(text)
        self.slot_id = slot_id
        self._editing = False

        # 스트로크
        self._stroke_width: float = 0.0
        self._stroke_color: QColor = QColor("#000000")

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        font = QFont(_default_korean_font() or "sans-serif", 24)
        self.setFont(font)
        self.setDefaultTextColor(QColor("#222222"))
        self.setTextWidth(400)  # 기본 너비

        # 리사이즈 핸들
        self._handles: dict[str, TextResizeHandle] = {}
        self._resizing = False
        self._resize_key = ""
        self._press_scene_pos = QPointF()
        self._press_width: float = 400
        self._press_font_size: int = 24
        for key in ('ml', 'mr', 'tl', 'tr', 'bl', 'br'):
            h = TextResizeHandle(key, self)
            self._handles[key] = h
        self._update_handles()
        self._show_handles(False)

    # ── 핸들 ─────────────────────────────────────────────────────────
    def _update_handles(self):
        r = self.boundingRect()
        w, h = r.width(), r.height()
        pos = {
            'ml': (0, h / 2), 'mr': (w, h / 2),
            'tl': (0, 0),     'tr': (w, 0),
            'bl': (0, h),     'br': (w, h),
        }
        for k, (x, y) in pos.items():
            self._handles[k].setPos(x, y)

    def _show_handles(self, v: bool):
        for h in self._handles.values():
            h.setVisible(v)

    # ── 페인팅 ───────────────────────────────────────────────────────
    def paint(self, painter: QPainter, option, widget=None):
        if self._stroke_width > 0:
            self._paint_stroked(painter)
        else:
            super().paint(painter, option, widget)

        if self.isSelected() and not self._editing:
            pen = QPen(QColor("#f59e0b"), 1.5, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawRect(self.boundingRect().adjusted(0, 0, -1, -1))

        if self.isSelected():
            self._update_handles()

    def _paint_stroked(self, painter: QPainter):
        """텍스트 각 줄에 외곽선(stroke)을 그린 후 내부 색상으로 채움"""
        doc = self.document()
        font = self.font()
        fill_color = self.defaultTextColor()

        painter.save()
        block = doc.begin()
        while block.isValid():
            layout = block.layout()
            if layout:
                for i in range(layout.lineCount()):
                    line = layout.lineAt(i)
                    raw = block.text()
                    start = line.textStart()
                    length = line.textLength()
                    line_text = raw[start: start + length].rstrip('\n')
                    if not line_text:
                        block = block.next()
                        continue
                    path = QPainterPath()
                    path.addText(line.position(), font, line_text)

                    sw = self._stroke_width * 2
                    pen = QPen(self._stroke_color, sw)
                    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
                    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                    painter.strokePath(path, pen)
                    painter.fillPath(path, QBrush(fill_color))
            block = block.next()
        painter.restore()

    # ── 편집 이벤트 ──────────────────────────────────────────────────
    def mouseDoubleClickEvent(self, event):
        self._editing = True
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        self.setFocus()
        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        self.setTextCursor(cursor)
        super().mouseDoubleClickEvent(event)

    def focusOutEvent(self, event):
        self._editing = False
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        cursor = self.textCursor()
        cursor.clearSelection()
        self.setTextCursor(cursor)
        super().focusOutEvent(event)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedChange:
            self._show_handles(bool(value))
        return super().itemChange(change, value)

    # ── 리사이즈 마우스 ──────────────────────────────────────────────
    def mousePressEvent(self, event):
        pos = event.pos()
        self._resizing = False
        for key, handle in self._handles.items():
            hr = QRectF(handle.pos().x() - HANDLE_SIZE, handle.pos().y() - HANDLE_SIZE,
                        HANDLE_SIZE * 2, HANDLE_SIZE * 2)
            if hr.contains(pos):
                self._resizing = True
                self._resize_key = key
                self._press_scene_pos = event.scenePos()
                self._press_width = self.textWidth() if self.textWidth() > 0 else self.boundingRect().width()
                self._press_font_size = self.font().pointSize()
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not self._resizing:
            super().mouseMoveEvent(event)
            return
        delta = event.scenePos() - self._press_scene_pos
        key = self._resize_key

        # 좌우 핸들 → 너비 조정
        if key in ('ml', 'mr'):
            dx = delta.x() if 'r' in key else -delta.x()
            new_w = max(self.MIN_WIDTH, self._press_width + dx)
            self.setTextWidth(new_w)

        # 코너 핸들 → 폰트 크기 비례 조정
        elif key in ('tl', 'tr', 'bl', 'br'):
            dx = delta.x() if 'r' in key else -delta.x()
            dy = delta.y() if 'b' in key else -delta.y()
            factor = max(dx, dy) / max(self._press_width, 1)
            new_size = max(6, int(self._press_font_size * (1 + factor)))
            font = self.font()
            font.setPointSize(new_size)
            self.setFont(font)

        self._update_handles()
        event.accept()

    def mouseReleaseEvent(self, event):
        self._resizing = False
        super().mouseReleaseEvent(event)

    def contextMenuEvent(self, event):
        if self._editing:
            super().contextMenuEvent(event)
            return
        menu = QMenu()
        menu.addAction("편집").triggered.connect(lambda: self.mouseDoubleClickEvent(event))
        menu.addAction("삭제").triggered.connect(lambda: self.scene().removeItem(self))
        menu.addSeparator()
        menu.addAction("맨 앞으로").triggered.connect(lambda: self.setZValue(self.zValue() + 1))
        menu.addAction("맨 뒤로").triggered.connect(lambda: self.setZValue(self.zValue() - 1))
        menu.exec(event.screenPos())

    # ── 속성 설정 ────────────────────────────────────────────────────
    def set_font_family(self, family: str):
        f = self.font(); f.setFamily(family); self.setFont(f)

    def set_font_size(self, size: int):
        f = self.font(); f.setPointSize(size); self.setFont(f)

    def set_bold(self, bold: bool):
        f = self.font(); f.setBold(bold); self.setFont(f)

    def set_italic(self, italic: bool):
        f = self.font(); f.setItalic(italic); self.setFont(f)

    def set_color(self, color: QColor):
        self.setDefaultTextColor(color)

    def set_stroke(self, width: float, color: QColor):
        self._stroke_width = width
        self._stroke_color = color
        self.update()

    def set_alignment(self, alignment: Qt.AlignmentFlag):
        from PyQt6.QtGui import QTextBlockFormat
        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        fmt = QTextBlockFormat()
        fmt.setAlignment(alignment)
        cursor.mergeBlockFormat(fmt)
        self.setTextCursor(cursor)

    # ── 직렬화 ───────────────────────────────────────────────────────
    def to_dict(self) -> dict:
        font = self.font()
        return {
            "type": "text",
            "slot_id": self.slot_id,
            "x": self.pos().x(),
            "y": self.pos().y(),
            "text_width": self.textWidth(),
            "content": self.toPlainText(),
            "font_family": font.family(),
            "font_size": font.pointSize(),
            "bold": font.bold(),
            "italic": font.italic(),
            "color": self.defaultTextColor().name(),
            "stroke_width": self._stroke_width,
            "stroke_color": self._stroke_color.name(),
            "z": self.zValue(),
        }
