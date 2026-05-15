from PyQt6.QtWidgets import QGraphicsTextItem, QGraphicsItem, QMenu
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import (
    QPen, QColor, QFont, QTextCursor, QTextCharFormat,
    QTextBlockFormat
)


class TextItem(QGraphicsTextItem):
    """더블클릭 편집 가능한 텍스트 레이어"""

    def __init__(self, text: str = "텍스트를 입력하세요", slot_id: str = ""):
        super().__init__(text)
        self.slot_id = slot_id
        self._editing = False

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        font = QFont("맑은 고딕", 24)
        font.setBold(False)
        self.setFont(font)
        self.setDefaultTextColor(QColor("#222222"))

    # ------------------------------------------------------------------
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

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        if self.isSelected() and not self._editing:
            pen = QPen(QColor("#3b82f6"), 1.5, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawRect(self.boundingRect().adjusted(0, 0, -1, -1))

    def contextMenuEvent(self, event):
        if self._editing:
            super().contextMenuEvent(event)
            return
        menu = QMenu()
        act_edit = menu.addAction("편집")
        act_delete = menu.addAction("삭제")
        act_top = menu.addAction("맨 앞으로")
        act_bottom = menu.addAction("맨 뒤로")
        chosen = menu.exec(event.screenPos())
        if chosen == act_edit:
            self.mouseDoubleClickEvent(event)
        elif chosen == act_delete:
            self.scene().removeItem(self)
        elif chosen == act_top:
            self.setZValue(self.zValue() + 1)
        elif chosen == act_bottom:
            self.setZValue(self.zValue() - 1)

    # ------------------------------------------------------------------
    def set_font_family(self, family: str):
        font = self.font()
        font.setFamily(family)
        self.setFont(font)

    def set_font_size(self, size: int):
        font = self.font()
        font.setPointSize(size)
        self.setFont(font)

    def set_bold(self, bold: bool):
        font = self.font()
        font.setBold(bold)
        self.setFont(font)

    def set_italic(self, italic: bool):
        font = self.font()
        font.setItalic(italic)
        self.setFont(font)

    def set_color(self, color: QColor):
        self.setDefaultTextColor(color)

    def set_alignment(self, alignment: Qt.AlignmentFlag):
        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        fmt = QTextBlockFormat()
        fmt.setAlignment(alignment)
        cursor.mergeBlockFormat(fmt)
        self.setTextCursor(cursor)

    # ------------------------------------------------------------------
    def to_dict(self) -> dict:
        font = self.font()
        return {
            "type": "text",
            "slot_id": self.slot_id,
            "x": self.pos().x(),
            "y": self.pos().y(),
            "content": self.toPlainText(),
            "font_family": font.family(),
            "font_size": font.pointSize(),
            "bold": font.bold(),
            "italic": font.italic(),
            "color": self.defaultTextColor().name(),
            "z": self.zValue(),
        }
