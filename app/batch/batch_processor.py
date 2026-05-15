from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QPixmap, QColor
from PyQt6.QtCore import QPointF

from app.template.template_model import TemplateModel
from app.template.template_manager import TemplateManager
from app.canvas.canvas_widget import CanvasScene
from app.export.exporter import export_image

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}


class BatchProcessor(QObject):
    progress = pyqtSignal(int, int)   # current, total
    finished = pyqtSignal(int)        # 완료 개수
    error = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    # ------------------------------------------------------------------
    def run_folder_batch(
        self,
        model: TemplateModel,
        image_folder: str,
        output_dir: str,
        fmt: str = "PNG",
        quality: int = 95,
    ):
        images = sorted([
            p for p in Path(image_folder).iterdir()
            if p.suffix.lower() in IMAGE_EXTS
        ])
        slots = model.image_slots
        if not slots:
            self.error.emit("템플릿에 이미지 슬롯이 없습니다.")
            return

        group_size = len(slots)
        total = len(images) // group_size
        if total == 0:
            self.error.emit("이미지 파일이 슬롯 수보다 적습니다.")
            return

        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        ext = fmt.lower().replace("jpeg", "jpg")
        count = 0

        for i in range(total):
            group = images[i * group_size:(i + 1) * group_size]
            scene = self._build_scene(model)

            for item in scene.get_layer_items():
                from app.canvas.image_item import ImageItem
                if isinstance(item, ImageItem):
                    slot_idx = next(
                        (j for j, s in enumerate(slots) if s.slot_id == item.slot_id), None
                    )
                    if slot_idx is not None and slot_idx < len(group):
                        px = QPixmap(str(group[slot_idx]))
                        if not px.isNull():
                            item.original_pixmap = px
                            item.update()

            qimg = scene.render_to_image()
            out_path = out_dir / f"output_{i + 1:04d}.{ext}"
            export_image(qimg, out_path, quality)
            count += 1
            self.progress.emit(count, total)

        self.finished.emit(count)

    # ------------------------------------------------------------------
    def run_csv_batch(
        self,
        model: TemplateModel,
        data_path: str,
        output_dir: str,
        fmt: str = "PNG",
        quality: int = 95,
    ):
        import pandas as pd
        path = Path(data_path)
        try:
            if path.suffix.lower() == ".csv":
                df = pd.read_csv(str(path), encoding="utf-8-sig")
            else:
                df = pd.read_excel(str(path))
        except Exception as e:
            self.error.emit(f"파일 읽기 실패: {e}")
            return

        total = len(df)
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        ext = fmt.lower().replace("jpeg", "jpg")
        count = 0

        for i, row in df.iterrows():
            scene = self._build_scene(model)

            for item in scene.get_layer_items():
                from app.canvas.text_item import TextItem
                if isinstance(item, TextItem):
                    col = item.slot_id
                    if col in row and str(row[col]) != "nan":
                        item.setPlainText(str(row[col]))

            qimg = scene.render_to_image()
            out_path = out_dir / f"output_{i + 1:04d}.{ext}"
            export_image(qimg, out_path, quality)
            count += 1
            self.progress.emit(count, total)

        self.finished.emit(count)

    # ------------------------------------------------------------------
    def _build_scene(self, model: TemplateModel) -> CanvasScene:
        from PyQt6.QtWidgets import QApplication
        scene = CanvasScene(model.canvas_w, model.canvas_h)
        TemplateManager.apply_to_scene(model, scene)
        return scene
