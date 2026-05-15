from PyQt6.QtWidgets import (
    QGraphicsPixmapItem, QGraphicsItem, QGraphicsRectItem,
    QGraphicsSceneMouseEvent, QMenu
)
from PyQt6.QtCore import Qt, QRectF, QPointF, QSizeF
from PyQt6.QtGui import QPen, QColor, QPixmap, QPainter, QCursor


HANDLE_SIZE = 10


class ResizeHandle(QGraphicsRectItem):
    """코너 리사이즈 핸들"""

    def __init__(self, position: str, parent):
        super().__init__(-HANDLE_SIZE / 2, -HANDLE_SIZE / 2, HANDLE_SIZE, HANDLE_SIZE, parent)
        self.position = position  # 'tl','tr','bl','br','ml','mr','mt','mb'
        self.setBrush(QColor("#ffffff"))
        self.setPen(QPen(QColor("#3b82f6"), 1.5))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations, False)
        self.setZValue(1000)
        cursor_map = {
            'tl': Qt.CursorShape.SizeFDiagCursor,
            'br': Qt.CursorShape.SizeFDiagCursor,
            'tr': Qt.CursorShape.SizeBDiagCursor,
            'bl': Qt.CursorShape.SizeBDiagCursor,
            'ml': Qt.CursorShape.SizeHorCursor,
            'mr': Qt.CursorShape.SizeHorCursor,
            'mt': Qt.CursorShape.SizeVerCursor,
            'mb': Qt.CursorShape.SizeVerCursor,
        }
        self.setCursor(cursor_map.get(position, Qt.CursorShape.SizeAllCursor))


class ImageItem(QGraphicsPixmapItem):
    """드래그/리사이즈 가능한 이미지 레이어"""

    MIN_SIZE = 30

    def __init__(self, pixmap: QPixmap, slot_id: str = ""):
        super().__init__(pixmap)
        self.slot_id = slot_id
        self.original_pixmap = pixmap
        self._w = float(pixmap.width())
        self._h = float(pixmap.height())

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.setTransformationMode(Qt.TransformationMode.SmoothTransformation)

        self._handles: dict[str, ResizeHandle] = {}
        self._resizing = False
        self._resize_pos = ""
        self._press_pos = QPointF()
        self._press_rect = QRectF()

        self._build_handles()
        self._update_handles()
        self._show_handles(False)

    # ------------------------------------------------------------------
    def _build_handles(self):
        positions = ['tl', 'tr', 'bl', 'br', 'ml', 'mr', 'mt', 'mb']
        for pos in positions:
            h = ResizeHandle(pos, self)
            self._handles[pos] = h

    def _update_handles(self):
        w, h = self._w, self._h
        positions = {
            'tl': (0, 0), 'tr': (w, 0),
            'bl': (0, h), 'br': (w, h),
            'ml': (0, h / 2), 'mr': (w, h / 2),
            'mt': (w / 2, 0), 'mb': (w / 2, h),
        }
        for pos, (x, y) in positions.items():
            self._handles[pos].setPos(x, y)

    def _show_handles(self, visible: bool):
        for h in self._handles.values():
            h.setVisible(visible)

    # ------------------------------------------------------------------
    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, self._w, self._h)

    def paint(self, painter, option, widget=None):
        scaled = self.original_pixmap.scaled(
            int(self._w), int(self._h),
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )
        sx = (scaled.width() - self._w) / 2
        sy = (scaled.height() - self._h) / 2
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.drawPixmap(
            QRectF(0, 0, self._w, self._h),
            scaled,
            QRectF(sx, sy, self._w, self._h)
        )
        if self.isSelected():
            pen = QPen(QColor("#3b82f6"), 2, Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            painter.drawRect(QRectF(1, 1, self._w - 2, self._h - 2))

    # ------------------------------------------------------------------
    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedChange:
            self._show_handles(bool(value))
        return super().itemChange(change, value)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        pos = event.pos()
        self._resizing = False
        self._resize_pos = ""
        for handle_pos, handle in self._handles.items():
            hr = QRectF(
                handle.pos().x() - HANDLE_SIZE,
                handle.pos().y() - HANDLE_SIZE,
                HANDLE_SIZE * 2,
                HANDLE_SIZE * 2
            )
            if hr.contains(pos):
                self._resizing = True
                self._resize_pos = handle_pos
                self._press_pos = event.scenePos()
                self._press_rect = QRectF(self.pos().x(), self.pos().y(), self._w, self._h)
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        if not self._resizing:
            super().mouseMoveEvent(event)
            return

        delta = event.scenePos() - self._press_pos
        dx, dy = delta.x(), delta.y()
        r = self._press_rect

        new_x, new_y = r.x(), r.y()
        new_w, new_h = r.width(), r.height()

        pos = self._resize_pos
        if 'l' in pos:
            new_x = r.x() + dx
            new_w = max(self.MIN_SIZE, r.width() - dx)
        if 'r' in pos:
            new_w = max(self.MIN_SIZE, r.width() + dx)
        if 't' in pos:
            new_y = r.y() + dy
            new_h = max(self.MIN_SIZE, r.height() - dy)
        if 'b' in pos:
            new_h = max(self.MIN_SIZE, r.height() + dy)

        self.setPos(new_x, new_y)
        self._w = new_w
        self._h = new_h
        self._update_handles()
        self.prepareGeometryChange()
        self.update()
        event.accept()

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        self._resizing = False
        super().mouseReleaseEvent(event)

    def contextMenuEvent(self, event):
        menu = QMenu()
        act_replace = menu.addAction("이미지 교체")
        act_delete = menu.addAction("삭제")
        act_top = menu.addAction("맨 앞으로")
        act_bottom = menu.addAction("맨 뒤로")
        chosen = menu.exec(event.screenPos())
        if chosen == act_replace:
            self.scene().views()[0].replace_image(self)
        elif chosen == act_delete:
            self.scene().removeItem(self)
        elif chosen == act_top:
            self.setZValue(self.zValue() + 1)
        elif chosen == act_bottom:
            self.setZValue(self.zValue() - 1)

    # ------------------------------------------------------------------
    def set_size(self, w: float, h: float):
        self._w = max(self.MIN_SIZE, w)
        self._h = max(self.MIN_SIZE, h)
        self._update_handles()
        self.prepareGeometryChange()
        self.update()

    def get_size(self):
        return self._w, self._h

    def to_dict(self) -> dict:
        return {
            "type": "image",
            "slot_id": self.slot_id,
            "x": self.pos().x(),
            "y": self.pos().y(),
            "width": self._w,
            "height": self._h,
            "z": self.zValue(),
        }
