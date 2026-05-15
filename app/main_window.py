from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QToolBar, QFileDialog, QInputDialog, QMessageBox,
    QDialog, QFormLayout, QComboBox, QSpinBox, QDialogButtonBox,
    QLabel, QColorDialog, QDockWidget, QListWidget, QListWidgetItem,
    QSlider, QGroupBox, QPushButton, QSplitter, QStatusBar,
    QMenu, QMenuBar
)
from PyQt6.QtCore import Qt, QSize, QPointF
from PyQt6.QtGui import (
    QAction, QIcon, QPixmap, QColor, QKeySequence, QFont
)

from app.canvas.canvas_widget import CanvasScene, CanvasView
from app.canvas.image_item import ImageItem
from app.canvas.text_item import TextItem
from app.canvas.frame_item import FrameItem
from app.template.template_manager import TemplateManager
from app.panels.property_panel import PropertyPanel
from app.panels.collage_dialog import CollageDialog
from app.export.exporter import export_image


CANVAS_PRESETS = {
    "인스타그램 정방형 (1080×1080)": (1080, 1080),
    "인스타그램 세로형 (1080×1350)": (1080, 1350),
    "유튜브 썸네일 (1280×720)": (1280, 720),
    "블로그 썸네일 (800×450)": (800, 450),
    "카카오채널 (1000×1000)": (1000, 1000),
    "사용자 지정": (0, 0),
}


class CanvasSizeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("캔버스 크기 설정")
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self._preset = QComboBox()
        self._preset.addItems(list(CANVAS_PRESETS.keys()))
        self._preset.currentIndexChanged.connect(self._on_preset)
        form.addRow("규격:", self._preset)

        self._w = QSpinBox()
        self._w.setRange(100, 9000)
        self._w.setValue(1080)
        self._w.setSuffix(" px")
        form.addRow("너비:", self._w)

        self._h = QSpinBox()
        self._h.setRange(100, 9000)
        self._h.setValue(1080)
        self._h.setSuffix(" px")
        form.addRow("높이:", self._h)

        layout.addLayout(form)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self._on_preset(0)

    def _on_preset(self, idx):
        name = self._preset.currentText()
        w, h = CANVAS_PRESETS[name]
        if w > 0:
            self._w.setValue(w)
            self._h.setValue(h)
            self._w.setEnabled(False)
            self._h.setEnabled(False)
        else:
            self._w.setEnabled(True)
            self._h.setEnabled(True)

    def get_size(self):
        return self._w.value(), self._h.value()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CardNews Editor")
        self.resize(1400, 900)
        self._current_template_path: Path | None = None

        self._scene = CanvasScene(1080, 1080)
        self._view = CanvasView(self._scene)
        self._view.setAcceptDrops(True)

        self._prop_panel = PropertyPanel()
        self._scene.item_selected.connect(self._prop_panel.update_for_item)

        self._setup_ui()
        self._setup_menu()
        self._setup_toolbar()
        self._view.fit_view()

    # ------------------------------------------------------------------
    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 캔버스 영역
        canvas_container = QWidget()
        cv_layout = QVBoxLayout(canvas_container)
        cv_layout.setContentsMargins(0, 0, 0, 0)
        cv_layout.addWidget(self._view)

        # 레이어 패널 (좌측)
        self._layer_list = QListWidget()
        self._layer_list.setMaximumWidth(180)
        self._layer_list.setMinimumWidth(150)
        self._layer_list.itemClicked.connect(self._on_layer_click)

        layer_dock = QWidget()
        ld = QVBoxLayout(layer_dock)
        ld.setContentsMargins(4, 4, 4, 4)
        ld.addWidget(QLabel("레이어"))
        ld.addWidget(self._layer_list)
        refresh_btn = QPushButton("새로고침")
        refresh_btn.clicked.connect(self._refresh_layers)
        ld.addWidget(refresh_btn)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(layer_dock)
        splitter.addWidget(canvas_container)
        splitter.addWidget(self._prop_panel)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)
        splitter.setSizes([165, 900, 240])

        main_layout.addWidget(splitter)

        self._status = QStatusBar()
        self.setStatusBar(self._status)
        self._update_status()
        self._scene.changed.connect(lambda _: self._update_status())

    def _setup_menu(self):
        mb = self.menuBar()

        # 파일
        file_menu = mb.addMenu("파일(&F)")
        act_new = QAction("새로 만들기", self, shortcut="Ctrl+N")
        act_new.triggered.connect(self._new_canvas)
        act_open_img = QAction("이미지 추가...", self, shortcut="Ctrl+O")
        act_open_img.triggered.connect(self._add_image)
        act_save = QAction("내보내기...", self, shortcut="Ctrl+S")
        act_save.triggered.connect(self._export)
        act_quit = QAction("종료", self, shortcut="Ctrl+Q")
        act_quit.triggered.connect(self.close)
        for a in [act_new, act_open_img, act_save, None, act_quit]:
            if a:
                file_menu.addAction(a)
            else:
                file_menu.addSeparator()

        # 템플릿
        tpl_menu = mb.addMenu("템플릿(&T)")
        act_save_tpl = QAction("템플릿으로 저장", self, shortcut="Ctrl+Shift+S")
        act_save_tpl.triggered.connect(self._save_template)
        act_load_tpl = QAction("템플릿 불러오기", self, shortcut="Ctrl+Shift+O")
        act_load_tpl.triggered.connect(self._load_template)
        tpl_menu.addAction(act_save_tpl)
        tpl_menu.addAction(act_load_tpl)

        # 편집
        edit_menu = mb.addMenu("편집(&E)")
        act_add_text = QAction("텍스트 추가", self, shortcut="Ctrl+T")
        act_add_text.triggered.connect(self._add_text)
        act_del = QAction("선택 항목 삭제", self, shortcut="Delete")
        act_del.triggered.connect(self._scene.remove_selected)
        act_bg_color = QAction("배경색 변경", self)
        act_bg_color.triggered.connect(self._change_bg_color)
        act_bg_image = QAction("배경 이미지 설정", self)
        act_bg_image.triggered.connect(self._set_bg_image)
        act_canvas_size = QAction("캔버스 크기 설정", self)
        act_canvas_size.triggered.connect(self._set_canvas_size)
        act_collage = QAction("콜라주 레이아웃 추가", self)
        act_collage.triggered.connect(self._add_collage_layout)
        for a in [act_add_text, act_del, None,
                  act_bg_color, act_bg_image, None,
                  act_canvas_size, None, act_collage]:
            if a:
                edit_menu.addAction(a)
            else:
                edit_menu.addSeparator()

        # 배치 처리
        batch_menu = mb.addMenu("배치 처리(&B)")
        act_batch = QAction("대량 처리 실행...", self)
        act_batch.triggered.connect(self._open_batch)
        batch_menu.addAction(act_batch)

        # 보기
        view_menu = mb.addMenu("보기(&V)")
        act_fit = QAction("캔버스 맞추기", self, shortcut="Ctrl+0")
        act_fit.triggered.connect(self._view.fit_view)
        act_refresh_layers = QAction("레이어 새로고침", self)
        act_refresh_layers.triggered.connect(self._refresh_layers)
        view_menu.addAction(act_fit)
        view_menu.addAction(act_refresh_layers)

    def _setup_toolbar(self):
        tb = QToolBar("도구")
        tb.setIconSize(QSize(20, 20))
        tb.setMovable(False)
        self.addToolBar(tb)

        def _act(text, shortcut=None, slot=None):
            a = QAction(text, self)
            if shortcut:
                a.setShortcut(shortcut)
            if slot:
                a.triggered.connect(slot)
            return a

        tb.addAction(_act("🖼 이미지 추가", "Ctrl+O", self._add_image))
        tb.addAction(_act("🔤 텍스트 추가", "Ctrl+T", self._add_text))
        tb.addAction(_act("▦ 콜라주 분할", None, self._add_collage_layout))
        tb.addSeparator()
        tb.addAction(_act("💾 내보내기", "Ctrl+S", self._export))
        tb.addSeparator()
        tb.addAction(_act("📋 템플릿 저장", "Ctrl+Shift+S", self._save_template))
        tb.addAction(_act("📂 템플릿 불러오기", "Ctrl+Shift+O", self._load_template))
        tb.addSeparator()
        tb.addAction(_act("⚡ 대량 처리", None, self._open_batch))
        tb.addSeparator()
        tb.addAction(_act("🔲 캔버스 크기", None, self._set_canvas_size))
        tb.addAction(_act("🎨 배경색", None, self._change_bg_color))
        tb.addSeparator()
        tb.addAction(_act("🔍 맞추기", "Ctrl+0", self._view.fit_view))

    # ------------------------------------------------------------------
    def _new_canvas(self):
        if QMessageBox.question(
            self, "새로 만들기", "현재 작업을 지우고 새로 시작하시겠습니까?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            self._scene.clear_canvas()
            self._current_template_path = None
            self._refresh_layers()

    def _add_image(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "이미지 선택", "",
            "이미지 파일 (*.png *.jpg *.jpeg *.webp *.bmp *.gif)"
        )
        for path in paths:
            px = QPixmap(path)
            if not px.isNull():
                self._scene.add_image(px, QPointF(50, 50))
        self._refresh_layers()

    def _add_text(self):
        self._scene.add_text("텍스트를 입력하세요", QPointF(100, 100))
        self._refresh_layers()

    def _add_collage_layout(self):
        w, h = self._scene.get_canvas_size()
        dlg = CollageDialog(w, h, self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        s = dlg.get_settings()
        rows, cols, gap = s["rows"], s["cols"], s["gap"]
        bw, bc = s["border_width"], s["border_color"]

        frame_w = (w - gap * (cols + 1)) / cols
        frame_h = (h - gap * (rows + 1)) / rows

        count = 0
        for r in range(rows):
            for c in range(cols):
                x = gap + c * (frame_w + gap)
                y = gap + r * (frame_h + gap)
                self._scene.add_frame(x, y, frame_w, frame_h,
                                      frame_id=f"frame_{count}",
                                      border_color=bc, border_width=bw)
                count += 1
        self._refresh_layers()
        self._status.showMessage(f"콜라주 프레임 {count}개 추가됨", 3000)

    def _change_bg_color(self):
        color = QColorDialog.getColor(self._scene._bg_color, self, "배경색 선택")
        if color.isValid():
            self._scene.set_bg_color(color)

    def _set_bg_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "배경 이미지 선택", "",
            "이미지 파일 (*.png *.jpg *.jpeg *.webp *.bmp)"
        )
        if path:
            self._scene.set_bg_image(QPixmap(path))

    def _set_canvas_size(self):
        dlg = CanvasSizeDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            w, h = dlg.get_size()
            self._scene.set_canvas_size(w, h)
            self._view.fit_view()
            self._update_status()

    # ------------------------------------------------------------------
    def _export(self):
        path, sel = QFileDialog.getSaveFileName(
            self, "이미지 내보내기", "output",
            "PNG (*.png);;JPEG (*.jpg);;WebP (*.webp)"
        )
        if not path:
            return

        fmt_map = {".png": "PNG", ".jpg": "JPEG", ".jpeg": "JPEG", ".webp": "WEBP"}
        ext = Path(path).suffix.lower()
        fmt = fmt_map.get(ext, "PNG")

        quality = 95
        if fmt in ("JPEG", "WEBP"):
            q, ok = QInputDialog.getInt(self, "품질 설정", "품질 (1~100):", 95, 1, 100)
            if ok:
                quality = q

        qimg = self._scene.render_to_image()
        export_image(qimg, path, quality)
        self._status.showMessage(f"저장 완료: {path}", 4000)

    # ------------------------------------------------------------------
    def _save_template(self):
        name, ok = QInputDialog.getText(self, "템플릿 저장", "템플릿 이름:")
        if not ok or not name.strip():
            return
        model = TemplateManager.snapshot_from_scene(self._scene, name.strip())
        path = TemplateManager.save(model)
        self._current_template_path = path
        self._status.showMessage(f"템플릿 저장: {path.name}", 4000)

    def _load_template(self):
        templates = TemplateManager.list_templates()
        if not templates:
            path, _ = QFileDialog.getOpenFileName(
                self, "템플릿 파일 선택", str(TemplateManager.__module__),
                "템플릿 (*.json)"
            )
            if not path:
                return
            from pathlib import Path as _Path
            templates = [_Path(path)]

        # 템플릿 선택 다이얼로그
        from PyQt6.QtWidgets import QInputDialog
        names = [p.stem for p in templates]
        chosen, ok = QInputDialog.getItem(
            self, "템플릿 불러오기", "템플릿 선택:", names, 0, False
        )
        if not ok:
            return
        idx = names.index(chosen)
        model = TemplateManager.load(templates[idx])
        TemplateManager.apply_to_scene(model, self._scene)
        self._view.fit_view()
        self._refresh_layers()
        self._status.showMessage(f"템플릿 불러옴: {chosen}", 4000)

    # ------------------------------------------------------------------
    def _open_batch(self):
        templates = TemplateManager.list_templates()
        if not templates:
            QMessageBox.warning(self, "경고", "저장된 템플릿이 없습니다.\n먼저 템플릿을 저장해주세요.")
            return

        names = [p.stem for p in templates]
        chosen, ok = QInputDialog.getItem(
            self, "배치 처리", "사용할 템플릿:", names, 0, False
        )
        if not ok:
            return
        idx = names.index(chosen)
        model = TemplateManager.load(templates[idx])

        from app.batch.batch_dialog import BatchDialog
        dlg = BatchDialog(model, self)
        dlg.exec()

    # ------------------------------------------------------------------
    def _refresh_layers(self):
        self._layer_list.clear()
        for item in self._scene.get_layer_items():
            if isinstance(item, TextItem):
                label = f"T  {item.toPlainText()[:18]}"
            elif isinstance(item, ImageItem):
                label = f"I  이미지 ({int(item.get_size()[0])}×{int(item.get_size()[1])})"
            elif isinstance(item, FrameItem):
                label = f"F  프레임 ({int(item.get_size()[0])}×{int(item.get_size()[1])})"
            else:
                label = "항목"
            list_item = QListWidgetItem(label)
            list_item.setData(Qt.ItemDataRole.UserRole, item)
            self._layer_list.addItem(list_item)

    def _on_layer_click(self, list_item: QListWidgetItem):
        item = list_item.data(Qt.ItemDataRole.UserRole)
        if item:
            self._scene.clearSelection()
            item.setSelected(True)
            self._prop_panel.update_for_item(item)

    def _update_status(self):
        w, h = self._scene.get_canvas_size()
        self._status.showMessage(f"캔버스: {w} × {h} px  |  Delete: 삭제  |  Ctrl+0: 맞추기  |  휠: 줌")
