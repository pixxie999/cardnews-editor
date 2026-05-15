from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox,
    QPushButton, QColorDialog, QFontComboBox, QCheckBox,
    QGroupBox, QSizePolicy, QComboBox, QSlider, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont

from app.canvas.text_item import TextItem
from app.canvas.image_item import ImageItem


class PropertyPanel(QWidget):
    """우측 속성 패널 — 선택된 아이템에 따라 동적으로 표시"""

    def __init__(self):
        super().__init__()
        self._current_item = None
        self.setMinimumWidth(230)
        self.setMaximumWidth(270)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        self._label_title = QLabel("속성")
        self._label_title.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(self._label_title)

        self._sep = QFrame()
        self._sep.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(self._sep)

        # 텍스트 속성 그룹
        self._text_group = self._build_text_group()
        layout.addWidget(self._text_group)

        # 이미지 속성 그룹
        self._image_group = self._build_image_group()
        layout.addWidget(self._image_group)

        layout.addStretch()
        self._set_visible(False, False)

    # ------------------------------------------------------------------
    def _build_text_group(self) -> QGroupBox:
        group = QGroupBox("텍스트 속성")
        layout = QVBoxLayout(group)
        layout.setSpacing(6)

        # 폰트 패밀리
        layout.addWidget(QLabel("폰트"))
        self._font_combo = QFontComboBox()
        self._font_combo.setCurrentFont(QFont("맑은 고딕"))
        self._font_combo.currentFontChanged.connect(self._on_font_family)
        layout.addWidget(self._font_combo)

        # 폰트 크기
        row = QHBoxLayout()
        row.addWidget(QLabel("크기"))
        self._font_size = QSpinBox()
        self._font_size.setRange(6, 300)
        self._font_size.setValue(24)
        self._font_size.valueChanged.connect(self._on_font_size)
        row.addWidget(self._font_size)
        layout.addLayout(row)

        # 굵기/기울임
        style_row = QHBoxLayout()
        self._bold_btn = QPushButton("B")
        self._bold_btn.setCheckable(True)
        self._bold_btn.setFixedWidth(36)
        self._bold_btn.setStyleSheet("font-weight: bold;")
        self._bold_btn.toggled.connect(self._on_bold)
        self._italic_btn = QPushButton("I")
        self._italic_btn.setCheckable(True)
        self._italic_btn.setFixedWidth(36)
        self._italic_btn.setStyleSheet("font-style: italic;")
        self._italic_btn.toggled.connect(self._on_italic)
        style_row.addWidget(self._bold_btn)
        style_row.addWidget(self._italic_btn)
        style_row.addStretch()
        layout.addLayout(style_row)

        # 정렬
        align_row = QHBoxLayout()
        self._align_left = QPushButton("≡")
        self._align_left.setFixedWidth(36)
        self._align_left.clicked.connect(lambda: self._on_align(Qt.AlignmentFlag.AlignLeft))
        self._align_center = QPushButton("≡")
        self._align_center.setFixedWidth(36)
        self._align_center.clicked.connect(lambda: self._on_align(Qt.AlignmentFlag.AlignHCenter))
        self._align_right = QPushButton("≡")
        self._align_right.setFixedWidth(36)
        self._align_right.clicked.connect(lambda: self._on_align(Qt.AlignmentFlag.AlignRight))
        align_row.addWidget(self._align_left)
        align_row.addWidget(self._align_center)
        align_row.addWidget(self._align_right)
        align_row.addStretch()
        layout.addLayout(align_row)

        # 텍스트 색상
        color_row = QHBoxLayout()
        color_row.addWidget(QLabel("색상"))
        self._text_color_btn = QPushButton()
        self._text_color_btn.setFixedSize(48, 24)
        self._text_color_btn.setStyleSheet("background: #222222; border: 1px solid #ccc;")
        self._text_color_btn.clicked.connect(self._on_text_color)
        color_row.addWidget(self._text_color_btn)
        color_row.addStretch()
        layout.addLayout(color_row)

        return group

    def _build_image_group(self) -> QGroupBox:
        group = QGroupBox("이미지 속성")
        layout = QVBoxLayout(group)
        layout.setSpacing(6)

        # 크기
        w_row = QHBoxLayout()
        w_row.addWidget(QLabel("너비"))
        self._img_w = QSpinBox()
        self._img_w.setRange(10, 9999)
        self._img_w.valueChanged.connect(self._on_img_size)
        w_row.addWidget(self._img_w)
        layout.addLayout(w_row)

        h_row = QHBoxLayout()
        h_row.addWidget(QLabel("높이"))
        self._img_h = QSpinBox()
        self._img_h.setRange(10, 9999)
        self._img_h.valueChanged.connect(self._on_img_size)
        h_row.addWidget(self._img_h)
        layout.addLayout(h_row)

        replace_btn = QPushButton("이미지 교체")
        replace_btn.clicked.connect(self._on_replace_image)
        layout.addWidget(replace_btn)

        return group

    # ------------------------------------------------------------------
    def update_for_item(self, item):
        self._current_item = item
        is_text = isinstance(item, TextItem)
        is_image = isinstance(item, ImageItem)
        self._set_visible(is_text, is_image)

        if is_text:
            self._label_title.setText("텍스트 속성")
            font = item.font()
            self._font_combo.blockSignals(True)
            self._font_combo.setCurrentFont(font)
            self._font_combo.blockSignals(False)
            self._font_size.blockSignals(True)
            self._font_size.setValue(font.pointSize())
            self._font_size.blockSignals(False)
            self._bold_btn.blockSignals(True)
            self._bold_btn.setChecked(font.bold())
            self._bold_btn.blockSignals(False)
            self._italic_btn.blockSignals(True)
            self._italic_btn.setChecked(font.italic())
            self._italic_btn.blockSignals(False)
            color = item.defaultTextColor()
            self._text_color_btn.setStyleSheet(
                f"background: {color.name()}; border: 1px solid #ccc;"
            )

        elif is_image:
            self._label_title.setText("이미지 속성")
            w, h = item.get_size()
            self._img_w.blockSignals(True)
            self._img_h.blockSignals(True)
            self._img_w.setValue(int(w))
            self._img_h.setValue(int(h))
            self._img_w.blockSignals(False)
            self._img_h.blockSignals(False)

        else:
            self._label_title.setText("속성")

    def _set_visible(self, text: bool, image: bool):
        self._text_group.setVisible(text)
        self._image_group.setVisible(image)

    # ------------------------------------------------------------------
    def _on_font_family(self, font: QFont):
        if isinstance(self._current_item, TextItem):
            self._current_item.set_font_family(font.family())

    def _on_font_size(self, size: int):
        if isinstance(self._current_item, TextItem):
            self._current_item.set_font_size(size)

    def _on_bold(self, checked: bool):
        if isinstance(self._current_item, TextItem):
            self._current_item.set_bold(checked)

    def _on_italic(self, checked: bool):
        if isinstance(self._current_item, TextItem):
            self._current_item.set_italic(checked)

    def _on_align(self, alignment: Qt.AlignmentFlag):
        if isinstance(self._current_item, TextItem):
            self._current_item.set_alignment(alignment)

    def _on_text_color(self):
        if not isinstance(self._current_item, TextItem):
            return
        color = QColorDialog.getColor(
            self._current_item.defaultTextColor(), self, "텍스트 색상 선택"
        )
        if color.isValid():
            self._current_item.set_color(color)
            self._text_color_btn.setStyleSheet(
                f"background: {color.name()}; border: 1px solid #ccc;"
            )

    def _on_img_size(self):
        if isinstance(self._current_item, ImageItem):
            self._current_item.set_size(self._img_w.value(), self._img_h.value())

    def _on_replace_image(self):
        if isinstance(self._current_item, ImageItem):
            from PyQt6.QtWidgets import QFileDialog
            path, _ = QFileDialog.getOpenFileName(
                self, "이미지 선택", "",
                "이미지 파일 (*.png *.jpg *.jpeg *.webp *.bmp)"
            )
            if path:
                from PyQt6.QtGui import QPixmap
                self._current_item.original_pixmap = QPixmap(path)
                self._current_item.update()
