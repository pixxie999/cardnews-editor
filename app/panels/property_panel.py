from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox,
    QPushButton, QColorDialog, QFontComboBox, QCheckBox,
    QGroupBox, QComboBox, QDoubleSpinBox, QFrame, QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QPixmap

from app.canvas.text_item import TextItem
from app.canvas.image_item import ImageItem
from app.canvas.frame_item import FrameItem


class PropertyPanel(QWidget):
    def __init__(self):
        super().__init__()
        self._current_item = None
        self.setMinimumWidth(235)
        self.setMaximumWidth(275)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        self._label_title = QLabel("속성")
        self._label_title.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(self._label_title)

        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(sep)

        self._text_group  = self._build_text_group()
        self._image_group = self._build_image_group()
        self._frame_group = self._build_frame_group()
        layout.addWidget(self._text_group)
        layout.addWidget(self._image_group)
        layout.addWidget(self._frame_group)
        layout.addStretch()

        self._set_visible(False, False, False)

    # ── 텍스트 속성 ──────────────────────────────────────────────────
    def _build_text_group(self) -> QGroupBox:
        group = QGroupBox("텍스트 속성")
        layout = QVBoxLayout(group)
        layout.setSpacing(5)

        layout.addWidget(QLabel("폰트"))
        self._font_combo = QFontComboBox()
        self._font_combo.currentFontChanged.connect(self._on_font_family)
        layout.addWidget(self._font_combo)

        row = QHBoxLayout()
        row.addWidget(QLabel("크기"))
        self._font_size = QSpinBox()
        self._font_size.setRange(6, 400)
        self._font_size.setValue(24)
        self._font_size.valueChanged.connect(self._on_font_size)
        row.addWidget(self._font_size)
        layout.addLayout(row)

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

        align_row = QHBoxLayout()
        for label, flag in [("≡L", Qt.AlignmentFlag.AlignLeft),
                             ("≡C", Qt.AlignmentFlag.AlignHCenter),
                             ("≡R", Qt.AlignmentFlag.AlignRight)]:
            btn = QPushButton(label)
            btn.setFixedWidth(36)
            btn.clicked.connect(lambda _, f=flag: self._on_align(f))
            align_row.addWidget(btn)
        align_row.addStretch()
        layout.addLayout(align_row)

        color_row = QHBoxLayout()
        color_row.addWidget(QLabel("글자색"))
        self._text_color_btn = QPushButton()
        self._text_color_btn.setFixedSize(48, 22)
        self._text_color_btn.setStyleSheet("background:#222222; border:1px solid #ccc;")
        self._text_color_btn.clicked.connect(self._on_text_color)
        color_row.addWidget(self._text_color_btn)
        color_row.addStretch()
        layout.addLayout(color_row)

        # ── 스트로크(외곽선) ─────────────────────────────────────────
        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(sep)
        layout.addWidget(QLabel("텍스트 외곽선"))

        sw_row = QHBoxLayout()
        sw_row.addWidget(QLabel("두께"))
        self._stroke_width = QDoubleSpinBox()
        self._stroke_width.setRange(0, 20)
        self._stroke_width.setSingleStep(0.5)
        self._stroke_width.setValue(0)
        self._stroke_width.setSuffix(" px")
        self._stroke_width.valueChanged.connect(self._on_stroke)
        sw_row.addWidget(self._stroke_width)
        layout.addLayout(sw_row)

        sc_row = QHBoxLayout()
        sc_row.addWidget(QLabel("색상"))
        self._stroke_color_btn = QPushButton()
        self._stroke_color_btn.setFixedSize(48, 22)
        self._stroke_color_btn.setStyleSheet("background:#000000; border:1px solid #ccc;")
        self._stroke_color_btn.clicked.connect(self._on_stroke_color)
        sc_row.addWidget(self._stroke_color_btn)
        sc_row.addStretch()
        layout.addLayout(sc_row)

        return group

    # ── 이미지 속성 ──────────────────────────────────────────────────
    def _build_image_group(self) -> QGroupBox:
        group = QGroupBox("이미지 속성")
        layout = QVBoxLayout(group)
        layout.setSpacing(5)

        wrow = QHBoxLayout()
        wrow.addWidget(QLabel("너비"))
        self._img_w = QSpinBox(); self._img_w.setRange(10, 9999)
        self._img_w.valueChanged.connect(self._on_img_size)
        wrow.addWidget(self._img_w)
        layout.addLayout(wrow)

        hrow = QHBoxLayout()
        hrow.addWidget(QLabel("높이"))
        self._img_h = QSpinBox(); self._img_h.setRange(10, 9999)
        self._img_h.valueChanged.connect(self._on_img_size)
        hrow.addWidget(self._img_h)
        layout.addLayout(hrow)

        btn = QPushButton("이미지 교체")
        btn.clicked.connect(self._on_replace_image)
        layout.addWidget(btn)
        return group

    # ── 프레임 속성 ──────────────────────────────────────────────────
    def _build_frame_group(self) -> QGroupBox:
        group = QGroupBox("프레임 속성")
        layout = QVBoxLayout(group)
        layout.setSpacing(5)

        wrow = QHBoxLayout()
        wrow.addWidget(QLabel("너비"))
        self._frame_w = QSpinBox(); self._frame_w.setRange(10, 9999)
        self._frame_w.valueChanged.connect(self._on_frame_size)
        wrow.addWidget(self._frame_w)
        layout.addLayout(wrow)

        hrow = QHBoxLayout()
        hrow.addWidget(QLabel("높이"))
        self._frame_h = QSpinBox(); self._frame_h.setRange(10, 9999)
        self._frame_h.valueChanged.connect(self._on_frame_size)
        hrow.addWidget(self._frame_h)
        layout.addLayout(hrow)

        bwrow = QHBoxLayout()
        bwrow.addWidget(QLabel("테두리"))
        self._frame_border_w = QDoubleSpinBox()
        self._frame_border_w.setRange(0, 30)
        self._frame_border_w.setSingleStep(0.5)
        self._frame_border_w.setSuffix(" px")
        self._frame_border_w.valueChanged.connect(self._on_frame_border)
        bwrow.addWidget(self._frame_border_w)
        layout.addLayout(bwrow)

        bcrow = QHBoxLayout()
        bcrow.addWidget(QLabel("테두리색"))
        self._frame_border_color_btn = QPushButton()
        self._frame_border_color_btn.setFixedSize(48, 22)
        self._frame_border_color_btn.setStyleSheet("background:#ffffff; border:1px solid #ccc;")
        self._frame_border_color_btn.clicked.connect(self._on_frame_border_color)
        bcrow.addWidget(self._frame_border_color_btn)
        bcrow.addStretch()
        layout.addLayout(bcrow)

        img_btn = QPushButton("이미지 추가/교체")
        img_btn.clicked.connect(self._on_frame_replace_image)
        layout.addWidget(img_btn)
        return group

    # ── 업데이트 ─────────────────────────────────────────────────────
    def update_for_item(self, item):
        self._current_item = item
        is_text  = isinstance(item, TextItem)
        is_image = isinstance(item, ImageItem)
        is_frame = isinstance(item, FrameItem)
        self._set_visible(is_text, is_image, is_frame)

        if is_text:
            self._label_title.setText("텍스트 속성")
            font = item.font()
            for widget, value in [
                (self._font_combo, font),
                (self._font_size,  font.pointSize()),
                (self._bold_btn,   font.bold()),
                (self._italic_btn, font.italic()),
            ]:
                widget.blockSignals(True)
                if isinstance(widget, QFontComboBox): widget.setCurrentFont(value)
                elif isinstance(widget, QSpinBox): widget.setValue(value)
                else: widget.setChecked(value)
                widget.blockSignals(False)
            c = item.defaultTextColor()
            self._text_color_btn.setStyleSheet(f"background:{c.name()}; border:1px solid #ccc;")
            self._stroke_width.blockSignals(True)
            self._stroke_width.setValue(item._stroke_width)
            self._stroke_width.blockSignals(False)
            self._stroke_color_btn.setStyleSheet(
                f"background:{item._stroke_color.name()}; border:1px solid #ccc;"
            )

        elif is_image:
            self._label_title.setText("이미지 속성")
            w, h = item.get_size()
            for sp, v in [(self._img_w, int(w)), (self._img_h, int(h))]:
                sp.blockSignals(True); sp.setValue(v); sp.blockSignals(False)

        elif is_frame:
            self._label_title.setText("프레임 속성")
            w, h = item.get_size()
            for sp, v in [(self._frame_w, int(w)), (self._frame_h, int(h))]:
                sp.blockSignals(True); sp.setValue(v); sp.blockSignals(False)
            self._frame_border_w.blockSignals(True)
            self._frame_border_w.setValue(item.border_width)
            self._frame_border_w.blockSignals(False)
            self._frame_border_color_btn.setStyleSheet(
                f"background:{item.border_color.name()}; border:1px solid #ccc;"
            )
        else:
            self._label_title.setText("속성")

    def _set_visible(self, text: bool, image: bool, frame: bool):
        self._text_group.setVisible(text)
        self._image_group.setVisible(image)
        self._frame_group.setVisible(frame)

    # ── 텍스트 핸들러 ─────────────────────────────────────────────────
    def _on_font_family(self, font: QFont):
        if isinstance(self._current_item, TextItem):
            self._current_item.set_font_family(font.family())

    def _on_font_size(self, size: int):
        if isinstance(self._current_item, TextItem):
            self._current_item.set_font_size(size)

    def _on_bold(self, v: bool):
        if isinstance(self._current_item, TextItem): self._current_item.set_bold(v)

    def _on_italic(self, v: bool):
        if isinstance(self._current_item, TextItem): self._current_item.set_italic(v)

    def _on_align(self, flag):
        if isinstance(self._current_item, TextItem): self._current_item.set_alignment(flag)

    def _on_text_color(self):
        if not isinstance(self._current_item, TextItem): return
        color = QColorDialog.getColor(self._current_item.defaultTextColor(), self, "글자색")
        if color.isValid():
            self._current_item.set_color(color)
            self._text_color_btn.setStyleSheet(f"background:{color.name()}; border:1px solid #ccc;")

    def _on_stroke(self, width: float):
        if isinstance(self._current_item, TextItem):
            self._current_item.set_stroke(width, self._current_item._stroke_color)

    def _on_stroke_color(self):
        if not isinstance(self._current_item, TextItem): return
        color = QColorDialog.getColor(self._current_item._stroke_color, self, "외곽선 색상")
        if color.isValid():
            self._current_item.set_stroke(self._current_item._stroke_width, color)
            self._stroke_color_btn.setStyleSheet(f"background:{color.name()}; border:1px solid #ccc;")

    # ── 이미지 핸들러 ─────────────────────────────────────────────────
    def _on_img_size(self):
        if isinstance(self._current_item, ImageItem):
            self._current_item.set_size(self._img_w.value(), self._img_h.value())

    def _on_replace_image(self):
        if not isinstance(self._current_item, ImageItem): return
        path, _ = QFileDialog.getOpenFileName(
            self, "이미지 선택", "", "이미지 파일 (*.png *.jpg *.jpeg *.webp *.bmp)"
        )
        if path:
            self._current_item.original_pixmap = QPixmap(path)
            self._current_item.update()

    # ── 프레임 핸들러 ─────────────────────────────────────────────────
    def _on_frame_size(self):
        if isinstance(self._current_item, FrameItem):
            self._current_item.set_size(self._frame_w.value(), self._frame_h.value())

    def _on_frame_border(self, w: float):
        if isinstance(self._current_item, FrameItem):
            self._current_item.border_width = w
            self._current_item.update()

    def _on_frame_border_color(self):
        if not isinstance(self._current_item, FrameItem): return
        color = QColorDialog.getColor(self._current_item.border_color, self, "테두리 색상")
        if color.isValid():
            self._current_item.border_color = color
            self._current_item.update()
            self._frame_border_color_btn.setStyleSheet(
                f"background:{color.name()}; border:1px solid #ccc;"
            )

    def _on_frame_replace_image(self):
        if not isinstance(self._current_item, FrameItem): return
        path, _ = QFileDialog.getOpenFileName(
            self, "이미지 선택", "", "이미지 파일 (*.png *.jpg *.jpeg *.webp *.bmp)"
        )
        if path:
            self._current_item.set_pixmap(QPixmap(path))
