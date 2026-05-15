"""
콜라주 레이아웃 설정 다이얼로그.
프리셋 또는 사용자 지정 행/열로 캔버스를 프레임으로 분할.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QSpinBox, QDoubleSpinBox, QPushButton, QDialogButtonBox,
    QGroupBox, QFormLayout, QColorDialog, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


PRESETS = {
    "좌우 2분할 (1행 × 2열)":  (1, 2),
    "상하 2분할 (2행 × 1열)":  (2, 1),
    "4분할 (2행 × 2열)":       (2, 2),
    "가로 3분할 (1행 × 3열)":  (1, 3),
    "세로 3분할 (3행 × 1열)":  (3, 1),
    "6분할 (2행 × 3열)":       (2, 3),
    "사용자 지정":              (0, 0),
}


class CollageDialog(QDialog):
    def __init__(self, canvas_w: int, canvas_h: int, parent=None):
        super().__init__(parent)
        self._canvas_w = canvas_w
        self._canvas_h = canvas_h
        self._border_color = QColor("#ffffff")

        self.setWindowTitle("콜라주 레이아웃 설정")
        self.setMinimumWidth(380)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # 프리셋
        form = QFormLayout()
        self._preset = QComboBox()
        self._preset.addItems(list(PRESETS.keys()))
        self._preset.currentIndexChanged.connect(self._on_preset)
        form.addRow("레이아웃:", self._preset)
        layout.addLayout(form)

        # 사용자 지정
        custom_group = QGroupBox("분할 설정")
        cg = QFormLayout(custom_group)

        self._rows = QSpinBox()
        self._rows.setRange(1, 10)
        self._rows.setValue(1)
        cg.addRow("행 수:", self._rows)

        self._cols = QSpinBox()
        self._cols.setRange(1, 10)
        self._cols.setValue(2)
        cg.addRow("열 수:", self._cols)

        self._gap = QSpinBox()
        self._gap.setRange(0, 100)
        self._gap.setValue(4)
        self._gap.setSuffix(" px")
        cg.addRow("프레임 간격:", self._gap)

        layout.addWidget(custom_group)

        # 테두리 설정
        border_group = QGroupBox("프레임 테두리")
        bg = QFormLayout(border_group)

        self._border_width = QDoubleSpinBox()
        self._border_width.setRange(0, 20)
        self._border_width.setValue(2.0)
        self._border_width.setSingleStep(0.5)
        self._border_width.setSuffix(" px")
        bg.addRow("테두리 두께:", self._border_width)

        color_row = QHBoxLayout()
        self._color_preview = QFrame()
        self._color_preview.setFixedSize(40, 22)
        self._color_preview.setStyleSheet("background: #ffffff; border: 1px solid #ccc;")
        color_btn = QPushButton("색상 선택")
        color_btn.clicked.connect(self._pick_color)
        color_row.addWidget(self._color_preview)
        color_row.addWidget(color_btn)
        color_row.addStretch()
        bg.addRow("테두리 색상:", color_row)

        layout.addWidget(border_group)

        # 미리보기 정보
        self._info = QLabel()
        self._info.setStyleSheet("color: #6b7280; font-size: 11px;")
        layout.addWidget(self._info)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._on_preset(0)
        self._rows.valueChanged.connect(self._update_info)
        self._cols.valueChanged.connect(self._update_info)
        self._gap.valueChanged.connect(self._update_info)

    def _on_preset(self, idx: int):
        name = self._preset.currentText()
        rows, cols = PRESETS[name]
        is_custom = (rows == 0)
        self._rows.setEnabled(is_custom)
        self._cols.setEnabled(is_custom)
        if not is_custom:
            self._rows.setValue(rows)
            self._cols.setValue(cols)
        self._update_info()

    def _pick_color(self):
        color = QColorDialog.getColor(self._border_color, self, "테두리 색상 선택")
        if color.isValid():
            self._border_color = color
            self._color_preview.setStyleSheet(
                f"background: {color.name()}; border: 1px solid #ccc;"
            )

    def _update_info(self):
        rows = self._rows.value()
        cols = self._cols.value()
        gap = self._gap.value()
        fw = (self._canvas_w - gap * (cols + 1)) / cols
        fh = (self._canvas_h - gap * (rows + 1)) / rows
        self._info.setText(
            f"프레임 크기: {fw:.0f} × {fh:.0f} px  |  총 {rows * cols}개"
        )

    def get_settings(self) -> dict:
        return {
            "rows": self._rows.value(),
            "cols": self._cols.value(),
            "gap": self._gap.value(),
            "border_width": self._border_width.value(),
            "border_color": self._border_color.name(),
        }
