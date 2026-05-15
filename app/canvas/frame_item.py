"""
콜라주 프레임 아이템 — 지정된 영역에 이미지를 클리핑해서 표시.
더블클릭 또는 우클릭으로 이미지 교체 가능.
"""
import platform
from PyQt6.QtWidgets import (
    QGraphicsItem, QGraphicsRectItem, QFileDialog, QMenu
)
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import (
    QPen, QColor, QBrush, QPixmap, QPainter,
    QPainterPath, QFont, QFontDatabase
)

HANDLE_SIZE = 10


def _sys_font():
    available = set(QFontDatabase.families())
    for name in (["Apple SD Gothic Neo", "맑은 고딕", "sans-serif"]):
        if name in available:
            return name
    return "sans-serif"


class FrameResizeHandle(QGraphicsRectItem):
    def __init__(self, pos_key: str, parent):
        super().__init__(-HANDLE_SIZE / 2, -HANDLE_SIZE / 2, HANDLE_SIZE, HANDLE_SIZE, parent)
        self.pos_key = pos_key
        self.setBrush(QColor("#ffffff"))
        self.setPen(QPen(QColor("#3b82f6"), 1.5))
        self.setZValue(2000)
        cursor_map = {
            'tl': Qt.CursorShape.SizeFDiagCursor, 'br': Qt.CursorShape.SizeFDiagCursor,
            'tr': Qt.CursorShape.SizeBDiagCursor, 'bl': Qt.CursorShape.SizeBDiagCursor,
            'ml': Qt.CursorShape.SizeHorCursor,   'mr': Qt.CursorShape.SizeHorCursor,
            'mt': Qt.CursorShape.SizeVerCursor,    'mb': Qt.CursorShape.SizeVerCursor,
        }
        self.setCursor(cursor_map.get(pos_key, Qt.CursorShape.SizeAllCursor))


class FrameItem(QGraphicsItem):
    """콜라주 프레임 — 고정 영역에 이미지를 cover 방식으로 표시"""

    MIN_SIZE = 30

    def __init__(self, width: float, height: float, frame_id: str = "",
                 border_color: str = "#ffffff", border_width: float = 2.0):
        super().__init__()
        self._w = width
        self._h = height
        self.frame_id = frame_id
        self.border_color = QColor(border_color)
        self.border_width = border_width
        self._pixmap: QPixmap | None = None

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

        # 리사이즈 핸들
        self._handles: dict[str, FrameResizeHandle] = {}
        self._resizing = False
        self._resize_key = ""
        self._press_scene_pos = QPointF()
        self._press_rect = QRectF()

        for key in ('tl', 'tr', 'bl', 'br', 'ml', 'mr', 'mt', 'mb'):
            h = FrameResizeHandle(key, self)
            self._handles[key] = h
        self._update_handles()
        self._show_handles(False)

    # ── 핸들 ──────────────────────────────────────────────────────────
    def _update_handles(self):
        w, h = self._w, self._h
        pos = {
            'tl': (0, 0), 'tr': (w, 0), 'bl': (0, h), 'br': (w, h),
            'ml': (0, h/2), 'mr': (w, h/2), 'mt': (w/2, 0), 'mb': (w/2, h),
        }
        for k, (x, y) in pos.items():
            self._handles[k].setPos(x, y)

    def _show_handles(self, v: bool):
        for h in self._handles.values():
            h.setVisible(v)

    # ── Qt 오버라이드 ─────────────────────────────────────────────────
    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, self._w, self._h)

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # 클리핑
        clip = QPainterPath()
        clip.addRect(QRectF(0, 0, self._w, self._h))
        painter.setClipPath(clip)

        # 이미지 또는 플레이스홀더
        if self._pixmap and not self._pixmap.isNull():
            scaled = self._pixmap.scaled(
                int(self._w), int(self._h),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            sx = (scaled.width() - self._w) / 2
            sy = (scaled.height() - self._h) / 2
            painter.drawPixmap(
                QRectF(0, 0, self._w, self._h),
                scaled,
                QRectF(sx, sy, self._w, self._h),
            )
        else:
            painter.fillRect(QRectF(0, 0, self._w, self._h), QColor("#e5e7eb"))
            painter.setPen(QPen(QColor("#9ca3af"), 1.5, Qt.PenStyle.DashLine))
            painter.drawLine(QPointF(0, 0), QPointF(self._w, self._h))
            painter.drawLine(QPointF(self._w, 0), QPointF(0, self._h))
            painter.setPen(QColor("#6b7280"))
            painter.setFont(QFont(_sys_font(), max(9, min(int(self._h / 8), 18))))
            painter.drawText(
                QRectF(0, 0, self._w, self._h),
                Qt.AlignmentFlag.AlignCenter,
                "더블클릭으로\n이미지 추가",
            )

        painter.setClipping(False)

        # 테두리
        if self.border_width > 0:
            pen = QPen(self.border_color, self.border_width)
            painter.setPen(pen)
            half = self.border_width / 2
            painter.drawRect(QRectF(half, half, self._w - self.border_width, self._h - self.border_width))

        # 선택 표시
        if self.isSelected():
            pen = QPen(QColor("#3b82f6"), 2)
            painter.setPen(pen)
            painter.drawRect(QRectF(1, 1, self._w - 2, self._h - 2))

    # ── 이벤트 ────────────────────────────────────────────────────────
    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedChange:
            self._show_handles(bool(value))
        return super().itemChange(change, value)

    def mouseDoubleClickEvent(self, event):
        self._open_image_dialog()
        event.accept()

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
                self._press_rect = QRectF(self.pos().x(), self.pos().y(), self._w, self._h)
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not self._resizing:
            super().mouseMoveEvent(event)
            return
        delta = event.scenePos() - self._press_scene_pos
        dx, dy = delta.x(), delta.y()
        r = self._press_rect
        nx, ny, nw, nh = r.x(), r.y(), r.width(), r.height()
        k = self._resize_key
        if 'l' in k: nx = r.x() + dx; nw = max(self.MIN_SIZE, r.width() - dx)
        if 'r' in k: nw = max(self.MIN_SIZE, r.width() + dx)
        if 't' in k: ny = r.y() + dy; nh = max(self.MIN_SIZE, r.height() - dy)
        if 'b' in k: nh = max(self.MIN_SIZE, r.height() + dy)
        self.setPos(nx, ny)
        self._w, self._h = nw, nh
        self._update_handles()
        self.prepareGeometryChange()
        self.update()
        event.accept()

    def mouseReleaseEvent(self, event):
        self._resizing = False
        super().mouseReleaseEvent(event)

    def contextMenuEvent(self, event):
        menu = QMenu()
        menu.addAction("이미지 추가/교체").triggered.connect(self._open_image_dialog)
        menu.addAction("이미지 제거").triggered.connect(self._clear_image)
        menu.addSeparator()
        menu.addAction("삭제").triggered.connect(lambda: self.scene().removeItem(self))
        menu.exec(event.screenPos())

    # ── 이미지 ────────────────────────────────────────────────────────
    def _open_image_dialog(self):
        path, _ = QFileDialog.getOpenFileName(
            None, "이미지 선택", "",
            "이미지 파일 (*.png *.jpg *.jpeg *.webp *.bmp *.gif)",
        )
        if path:
            self.set_pixmap(QPixmap(path))

    def _clear_image(self):
        self._pixmap = None
        self.update()

    def set_pixmap(self, pixmap: QPixmap):
        self._pixmap = pixmap
        self.update()

    def set_size(self, w: float, h: float):
        self._w = max(self.MIN_SIZE, w)
        self._h = max(self.MIN_SIZE, h)
        self._update_handles()
        self.prepareGeometryChange()
        self.update()

    def get_size(self):
        return self._w, self._h

    # ── 직렬화 ────────────────────────────────────────────────────────
    def to_dict(self) -> dict:
        return {
            "type": "frame",
            "frame_id": self.frame_id,
            "x": self.pos().x(),
            "y": self.pos().y(),
            "width": self._w,
            "height": self._h,
            "border_color": self.border_color.name(),
            "border_width": self.border_width,
            "z": self.zValue(),
        }
