from PyQt6.QtWidgets import (
    QGraphicsScene, QGraphicsView, QGraphicsRectItem,
    QFileDialog, QApplication
)
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal
from PyQt6.QtGui import (
    QColor, QPen, QBrush, QPixmap, QWheelEvent,
    QKeyEvent, QImage, QPainter
)

from app.canvas.image_item import ImageItem
from app.canvas.text_item import TextItem


class CanvasScene(QGraphicsScene):
    """편집 캔버스 씬"""

    item_selected = pyqtSignal(object)   # 선택된 아이템 → 속성 패널 업데이트

    def __init__(self, width: int = 1080, height: int = 1080):
        super().__init__()
        self._canvas_w = width
        self._canvas_h = height
        self._bg_color = QColor("#ffffff")
        self._bg_image: QPixmap | None = None

        self.setSceneRect(0, 0, width, height)
        self._draw_bg()

    # ------------------------------------------------------------------
    def _draw_bg(self):
        for item in self.items():
            if getattr(item, "_is_bg", False):
                self.removeItem(item)

        bg = QGraphicsRectItem(0, 0, self._canvas_w, self._canvas_h)
        bg._is_bg = True
        bg.setZValue(-9999)
        bg.setFlag(bg.GraphicsItemFlag.ItemIsSelectable, False)
        bg.setFlag(bg.GraphicsItemFlag.ItemIsMovable, False)

        if self._bg_image:
            scaled = self._bg_image.scaled(
                self._canvas_w, self._canvas_h,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            bg.setBrush(QBrush(scaled))
        else:
            bg.setBrush(QBrush(self._bg_color))
        bg.setPen(QPen(Qt.PenStyle.NoPen))
        self.addItem(bg)

    # ------------------------------------------------------------------
    def set_canvas_size(self, width: int, height: int):
        self._canvas_w = width
        self._canvas_h = height
        self.setSceneRect(0, 0, width, height)
        self._draw_bg()

    def set_bg_color(self, color: QColor):
        self._bg_color = color
        self._bg_image = None
        self._draw_bg()

    def set_bg_image(self, pixmap: QPixmap):
        self._bg_image = pixmap
        self._draw_bg()

    def get_canvas_size(self):
        return self._canvas_w, self._canvas_h

    # ------------------------------------------------------------------
    def add_image(self, pixmap: QPixmap, pos: QPointF = QPointF(0, 0),
                  w: float = 0, h: float = 0, slot_id: str = "") -> ImageItem:
        item = ImageItem(pixmap, slot_id)
        if w > 0 and h > 0:
            item.set_size(w, h)
        self.addItem(item)
        item.setPos(pos)
        item.setZValue(self._next_z())
        return item

    def add_text(self, text: str = "텍스트를 입력하세요",
                 pos: QPointF = QPointF(50, 50), slot_id: str = "") -> TextItem:
        item = TextItem(text, slot_id)
        self.addItem(item)
        item.setPos(pos)
        item.setZValue(self._next_z())
        return item

    def _next_z(self) -> float:
        z_values = [it.zValue() for it in self.items()
                    if not getattr(it, "_is_bg", False)]
        return max(z_values, default=0) + 1

    # ------------------------------------------------------------------
    def remove_selected(self):
        for item in self.selectedItems():
            self.removeItem(item)

    def clear_canvas(self):
        for item in self.items():
            if not getattr(item, "_is_bg", False):
                self.removeItem(item)

    # ------------------------------------------------------------------
    def get_layer_items(self) -> list:
        return [it for it in sorted(self.items(), key=lambda x: -x.zValue())
                if not getattr(it, "_is_bg", False)]

    def selectionChanged_handler(self):
        selected = self.selectedItems()
        if selected:
            self.item_selected.emit(selected[0])
        else:
            self.item_selected.emit(None)

    # ------------------------------------------------------------------
    def to_dict(self) -> dict:
        layers = []
        for item in self.get_layer_items():
            if hasattr(item, "to_dict"):
                layers.append(item.to_dict())
        return {
            "canvas_w": self._canvas_w,
            "canvas_h": self._canvas_h,
            "bg_color": self._bg_color.name(),
            "layers": layers,
        }

    # ------------------------------------------------------------------
    def render_to_image(self) -> QImage:
        image = QImage(self._canvas_w, self._canvas_h, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.render(painter, QRectF(0, 0, self._canvas_w, self._canvas_h),
                    QRectF(0, 0, self._canvas_w, self._canvas_h))
        painter.end()
        return image


class CanvasView(QGraphicsView):
    """캔버스 뷰 — 줌/패닝 지원"""

    def __init__(self, scene: CanvasScene):
        super().__init__(scene)
        self._canvas_scene = scene
        self._zoom = 1.0

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setBackgroundBrush(QBrush(QColor("#2d2d2d")))

        # 외곽 그림자 효과 (체커보드 배경)
        self.setStyleSheet("border: none;")

        scene.selectionChanged.connect(scene.selectionChanged_handler)

    # ------------------------------------------------------------------
    def wheelEvent(self, event: QWheelEvent):
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self._zoom *= factor
        self._zoom = max(0.1, min(self._zoom, 8.0))
        self.setTransform(self.transform().scale(factor, factor))

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Delete:
            self._canvas_scene.remove_selected()
        elif event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_0:
                self.reset_zoom()
        else:
            super().keyPressEvent(event)

    def reset_zoom(self):
        self.resetTransform()
        self._zoom = 1.0
        self.fitInView(self._canvas_scene.sceneRect(),
                       Qt.AspectRatioMode.KeepAspectRatio)

    def fit_view(self):
        self.fitInView(self._canvas_scene.sceneRect(),
                       Qt.AspectRatioMode.KeepAspectRatio)
        self._zoom = 1.0

    # ------------------------------------------------------------------
    def replace_image(self, item: ImageItem):
        path, _ = QFileDialog.getOpenFileName(
            self, "이미지 선택", "",
            "이미지 파일 (*.png *.jpg *.jpeg *.webp *.bmp *.gif)"
        )
        if path:
            pixmap = QPixmap(path)
            item.original_pixmap = pixmap
            item.update()

    # ------------------------------------------------------------------
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif')):
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    scene_pos = self.mapToScene(event.position().toPoint())
                    self._canvas_scene.add_image(pixmap, scene_pos)
        event.acceptProposedAction()
