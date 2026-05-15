# Skills — 기능 구현 참조

## SK-001 | 캔버스 레이어 시스템

**목적**: PyQt6 QGraphicsScene 기반으로 이미지/텍스트 레이어를 마우스로 조작

```python
# 이미지 아이템 (드래그, 리사이즈)
class ImageItem(QGraphicsPixmapItem):
    def __init__(self, pixmap):
        super().__init__(pixmap)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

# 텍스트 아이템 (더블클릭 편집)
class TextItem(QGraphicsTextItem):
    def mouseDoubleClickEvent(self, event):
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        super().mouseDoubleClickEvent(event)
```

---

## SK-002 | 템플릿 JSON 구조

**목적**: 템플릿을 JSON으로 직렬화/역직렬화

```json
{
  "name": "유튜브 썸네일 기본",
  "canvas": { "width": 1280, "height": 720, "bg_color": "#ffffff" },
  "image_slots": [
    { "id": "img_0", "x": 0, "y": 0, "width": 800, "height": 720, "fit": "cover" }
  ],
  "text_slots": [
    {
      "id": "txt_0", "x": 820, "y": 100, "width": 440, "height": 80,
      "content": "제목을 입력하세요",
      "font_family": "맑은 고딕", "font_size": 48,
      "bold": true, "color": "#222222", "align": "left"
    }
  ]
}
```

---

## SK-003 | PC 설치 폰트 불러오기

**목적**: 시스템에 설치된 폰트 목록을 콤보박스에 표시

```python
from PyQt6.QtGui import QFontDatabase

def get_system_fonts():
    db = QFontDatabase()
    return sorted(db.families())

# 콤보박스에 적용
font_combo = QFontComboBox()
font_combo.currentFontChanged.connect(on_font_changed)
```

---

## SK-004 | Pillow 이미지 내보내기

**목적**: QGraphicsScene → PIL Image → 파일 저장

```python
from PIL import Image
import io
from PyQt6.QtCore import QBuffer, QByteArray

def export_scene(scene, path, fmt="PNG", quality=95):
    rect = scene.sceneRect()
    image = QImage(int(rect.width()), int(rect.height()), QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    scene.render(painter)
    painter.end()

    buf = QBuffer()
    buf.open(QBuffer.OpenModeFlag.ReadWrite)
    image.save(buf, "PNG")
    pil_img = Image.open(io.BytesIO(buf.data().data()))

    if fmt.upper() == "JPG":
        pil_img = pil_img.convert("RGB")
    pil_img.save(path, format=fmt, quality=quality)
```

---

## SK-005 | CSV/Excel 배치 처리

**목적**: 데이터 파일에서 행을 읽어 텍스트 슬롯에 매핑 후 일괄 저장

```python
import pandas as pd

def run_batch_from_datafile(template, data_path, output_dir, fmt="PNG"):
    df = pd.read_csv(data_path) if data_path.endswith(".csv") \
         else pd.read_excel(data_path)
    
    for i, row in df.iterrows():
        # 텍스트 슬롯 ID와 컬럼명 매핑
        for slot in template["text_slots"]:
            col = slot["id"]  # 컬럼명 = 슬롯 ID
            if col in row:
                slot["content"] = str(row[col])
        render_and_save(template, output_dir / f"output_{i:04d}.{fmt.lower()}")
```

---

## SK-006 | 폴더 기반 배치 처리

**목적**: 이미지 폴더 → 템플릿 슬롯 순서대로 자동 매핑

```python
from pathlib import Path

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

def run_batch_from_folder(template, image_folder, output_dir, fmt="PNG"):
    images = sorted([p for p in Path(image_folder).iterdir()
                     if p.suffix.lower() in IMAGE_EXTS])
    slots = template["image_slots"]
    group_size = len(slots)

    for i in range(0, len(images), group_size):
        group = images[i:i + group_size]
        for slot, img_path in zip(slots, group):
            slot["source"] = str(img_path)
        render_and_save(template, output_dir / f"output_{i // group_size:04d}.{fmt.lower()}")
```

---

## SK-007 | PyInstaller .exe 빌드

**목적**: 단일 실행 파일로 패키징

```bat
REM build.bat
pyinstaller ^
  --onefile ^
  --windowed ^
  --name "CardNewsEditor" ^
  --icon "assets/icons/app.ico" ^
  --add-data "assets;assets" ^
  --add-data "templates;templates" ^
  main.py
```

**주의사항**:
- `--windowed` 플래그로 콘솔 창 숨김
- 폰트는 시스템 폰트 사용이므로 별도 번들 불필요
- PyQt6 플러그인 자동 포함 확인: `qt6_applications` 의존성

---

## SK-008 | 이미지 슬롯 클리핑 (Cover Fit)

**목적**: 이미지를 슬롯 영역에 맞게 잘라서 표시 (object-fit: cover 동작)

```python
def fit_pixmap_to_slot(pixmap, slot_w, slot_h):
    scaled = pixmap.scaled(
        slot_w, slot_h,
        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
        Qt.TransformationMode.SmoothTransformation
    )
    x = (scaled.width() - slot_w) // 2
    y = (scaled.height() - slot_h) // 2
    return scaled.copy(x, y, slot_w, slot_h)
```
