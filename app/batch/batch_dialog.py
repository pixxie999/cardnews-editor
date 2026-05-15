from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QLineEdit, QPushButton, QComboBox, QSpinBox,
    QProgressBar, QFileDialog, QMessageBox, QGroupBox,
    QFormLayout
)
from PyQt6.QtCore import QThread, pyqtSignal, QObject
from PyQt6.QtGui import QColor

from app.template.template_model import TemplateModel
from app.batch.batch_processor import BatchProcessor


class _WorkerThread(QThread):
    def __init__(self, processor: BatchProcessor, mode: str, kwargs: dict):
        super().__init__()
        self._processor = processor
        self._mode = mode
        self._kwargs = kwargs

    def run(self):
        if self._mode == "folder":
            self._processor.run_folder_batch(**self._kwargs)
        else:
            self._processor.run_csv_batch(**self._kwargs)


class BatchDialog(QDialog):
    def __init__(self, model: TemplateModel, parent=None):
        super().__init__(parent)
        self._model = model
        self._processor = BatchProcessor()
        self._thread: _WorkerThread | None = None

        self.setWindowTitle("대량 처리")
        self.setMinimumSize(520, 420)
        self._build_ui()
        self._connect()

    # ------------------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)
        self._tabs = QTabWidget()

        # ── 폴더 기반 탭 ──────────────────────────────────────────────
        folder_tab = QWidget()
        fl = QVBoxLayout(folder_tab)
        form = QFormLayout()

        self._folder_path = QLineEdit()
        self._folder_path.setPlaceholderText("이미지 폴더 경로")
        folder_btn = QPushButton("찾아보기")
        folder_btn.clicked.connect(self._browse_folder)
        row = QHBoxLayout()
        row.addWidget(self._folder_path)
        row.addWidget(folder_btn)
        form.addRow("이미지 폴더:", row)

        self._folder_out = QLineEdit()
        self._folder_out.setPlaceholderText("저장 폴더 경로")
        folder_out_btn = QPushButton("찾아보기")
        folder_out_btn.clicked.connect(lambda: self._browse_output(self._folder_out))
        row2 = QHBoxLayout()
        row2.addWidget(self._folder_out)
        row2.addWidget(folder_out_btn)
        form.addRow("저장 폴더:", row2)

        fl.addLayout(form)

        slot_info = QLabel(
            f"ℹ 템플릿 이미지 슬롯 수: {len(model.image_slots)}개\n"
            f"   이미지 파일을 슬롯 수({len(model.image_slots)})개씩 묶어서 처리합니다."
        )
        slot_info.setStyleSheet("color: #6b7280; font-size: 11px;")
        fl.addWidget(slot_info)
        fl.addStretch()
        self._tabs.addTab(folder_tab, "폴더 기반")

        # ── CSV/Excel 탭 ──────────────────────────────────────────────
        csv_tab = QWidget()
        cl = QVBoxLayout(csv_tab)
        cform = QFormLayout()

        self._csv_path = QLineEdit()
        self._csv_path.setPlaceholderText("CSV 또는 Excel 파일 경로")
        csv_btn = QPushButton("찾아보기")
        csv_btn.clicked.connect(self._browse_csv)
        crow = QHBoxLayout()
        crow.addWidget(self._csv_path)
        crow.addWidget(csv_btn)
        cform.addRow("데이터 파일:", crow)

        self._csv_out = QLineEdit()
        self._csv_out.setPlaceholderText("저장 폴더 경로")
        csv_out_btn = QPushButton("찾아보기")
        csv_out_btn.clicked.connect(lambda: self._browse_output(self._csv_out))
        crow2 = QHBoxLayout()
        crow2.addWidget(self._csv_out)
        crow2.addWidget(csv_out_btn)
        cform.addRow("저장 폴더:", crow2)

        cl.addLayout(cform)

        slot_names = [s.slot_id for s in model.text_slots]
        csv_info = QLabel(
            f"ℹ 텍스트 슬롯 ID (CSV 컬럼명과 일치시키세요):\n   {', '.join(slot_names) if slot_names else '없음'}"
        )
        csv_info.setStyleSheet("color: #6b7280; font-size: 11px;")
        cl.addWidget(csv_info)
        cl.addStretch()
        self._tabs.addTab(csv_tab, "CSV / Excel 기반")

        layout.addWidget(self._tabs)

        # ── 공통 옵션 ────────────────────────────────────────────────
        opt_group = QGroupBox("저장 옵션")
        opt_layout = QFormLayout(opt_group)

        self._fmt_combo = QComboBox()
        self._fmt_combo.addItems(["PNG", "JPG", "WEBP"])
        opt_layout.addRow("저장 포맷:", self._fmt_combo)

        self._quality_spin = QSpinBox()
        self._quality_spin.setRange(1, 100)
        self._quality_spin.setValue(95)
        opt_layout.addRow("품질 (JPG/WEBP):", self._quality_spin)

        layout.addWidget(opt_group)

        # ── 진행률 ───────────────────────────────────────────────────
        self._progress = QProgressBar()
        self._progress.setValue(0)
        layout.addWidget(self._progress)

        self._status_label = QLabel("")
        layout.addWidget(self._status_label)

        # ── 버튼 ────────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        self._run_btn = QPushButton("실행")
        self._run_btn.setDefault(True)
        close_btn = QPushButton("닫기")
        close_btn.clicked.connect(self.close)
        btn_row.addStretch()
        btn_row.addWidget(self._run_btn)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

    def _connect(self):
        self._run_btn.clicked.connect(self._run)
        self._processor.progress.connect(self._on_progress)
        self._processor.finished.connect(self._on_finished)
        self._processor.error.connect(self._on_error)

    # ------------------------------------------------------------------
    def _browse_folder(self):
        d = QFileDialog.getExistingDirectory(self, "이미지 폴더 선택")
        if d:
            self._folder_path.setText(d)

    def _browse_csv(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "데이터 파일 선택", "",
            "데이터 파일 (*.csv *.xlsx *.xls)"
        )
        if path:
            self._csv_path.setText(path)

    def _browse_output(self, line_edit: QLineEdit):
        d = QFileDialog.getExistingDirectory(self, "저장 폴더 선택")
        if d:
            line_edit.setText(d)

    # ------------------------------------------------------------------
    def _run(self):
        fmt = self._fmt_combo.currentText()
        quality = self._quality_spin.value()
        tab = self._tabs.currentIndex()

        if tab == 0:
            folder = self._folder_path.text().strip()
            out = self._folder_out.text().strip()
            if not folder or not out:
                QMessageBox.warning(self, "경고", "폴더 경로를 모두 입력해주세요.")
                return
            kwargs = dict(model=self._model, image_folder=folder,
                          output_dir=out, fmt=fmt, quality=quality)
            mode = "folder"
        else:
            csv = self._csv_path.text().strip()
            out = self._csv_out.text().strip()
            if not csv or not out:
                QMessageBox.warning(self, "경고", "파일 경로를 모두 입력해주세요.")
                return
            kwargs = dict(model=self._model, data_path=csv,
                          output_dir=out, fmt=fmt, quality=quality)
            mode = "csv"

        self._run_btn.setEnabled(False)
        self._progress.setValue(0)
        self._status_label.setText("처리 중...")
        self._thread = _WorkerThread(self._processor, mode, kwargs)
        self._thread.start()

    def _on_progress(self, current: int, total: int):
        self._progress.setMaximum(total)
        self._progress.setValue(current)
        self._status_label.setText(f"{current} / {total} 처리 완료")

    def _on_finished(self, count: int):
        self._run_btn.setEnabled(True)
        self._status_label.setText(f"완료: {count}개 파일 저장")
        QMessageBox.information(self, "완료", f"{count}개 파일이 저장되었습니다.")

    def _on_error(self, msg: str):
        self._run_btn.setEnabled(True)
        self._status_label.setText(f"오류: {msg}")
        QMessageBox.critical(self, "오류", msg)
