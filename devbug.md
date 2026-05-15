# DevBug Log — 개발 이슈 및 변경 기록

> 작업 중 발생한 오류, 수정, 보완, 개선사항을 여기에 기록합니다.
> 형식: `[날짜] [유형] 내용`
> 유형: BUG / FIX / IMPROVE / NOTE / WARN

---

## 2026-05-15

### [NOTE] 프로젝트 초기화
- 프로젝트 구조 설계 완료
- claude.md / skills.md / devbug.md 생성
- 기술 스택 확정: PyQt6 + Pillow + openpyxl + pandas + PyInstaller

### [NOTE] 개발 환경 요구사항
- Python 3.11+ 권장 (PyQt6 호환성)
- Windows 10/11 타겟
- 가상환경(venv) 사용 권장

---

### [NOTE] 전체 구현 완료 (1단계~7단계)
- 구현 파일: main.py, app/ 하위 18개 파일
- 구문 검사: python3 ast.parse 전체 통과
- GitHub push 완료: pixxie999/cardnews-editor

### [NOTE] 실행 방법 (Windows)
```
pip install PyQt6 Pillow pandas openpyxl
python main.py
```

### [NOTE] .exe 빌드 방법 (Windows)
```
pip install pyinstaller
build.bat 실행
```

### [WARN] Mac 환경에서는 실행 테스트 불가
- PyQt6 GUI는 Windows 타겟이므로 Mac에서 UI 확인 불가
- Windows PC에서 직접 실행하여 테스트 필요

---

## 2026-05-15 (수정사항 2차)

### [BUG→FIX] 템플릿 저장 시 앱 종료
- **원인**: `scene.items()`가 ImageItem의 자식인 ResizeHandle을 포함 반환.
  `snapshot_from_scene`에서 `item.to_dict()` 호출 → AttributeError로 앱 크래시.
- **수정**: `get_layer_items()`에 `it.parentItem() is None` 조건 추가로 자식 아이템 제외.
- **파일**: `canvas_widget.py`

### [NEW] 콜라주 프레임 분할 기능
- `FrameItem` 클래스 신규 생성 (`app/canvas/frame_item.py`)
  - 지정 영역에 이미지를 cover 방식으로 클리핑 표시
  - 더블클릭/우클릭으로 이미지 교체, 테두리 색상/두께 설정 가능
  - 8방향 리사이즈 핸들
- `CollageDialog` 신규 생성 (`app/panels/collage_dialog.py`)
  - 프리셋 6종 (2분할~6분할) + 사용자 지정 행/열/간격
- `TemplateModel`에 `FrameSlot` 추가, 저장/불러오기 지원

### [NEW] 텍스트 외곽선(스트로크) 기능
- TextItem에 `_stroke_width`, `_stroke_color` 속성 추가
- `paint()` 오버라이드: QPainterPath로 각 글자에 외곽선 후 내부 채움
- 속성 패널에 외곽선 두께/색상 설정 UI 추가

### [NEW] 마우스로 텍스트 크기 조정
- TextItem에 6방향 리사이즈 핸들 추가
  - 좌/우 핸들: 텍스트 박스 너비 조정 (줄바꿈)
  - 코너 핸들: 폰트 크기 비례 조정

### [FIX] QPen.setAlignment AttributeError
- **원인**: FrameItem.paint에서 QPen에 없는 메서드 호출
- **수정**: 해당 라인 제거, drawRect 좌표로 직접 처리

<!-- 이후 작업 진행하면서 아래에 계속 추가 -->
