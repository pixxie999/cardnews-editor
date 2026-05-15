# CardNews Editor — 프로젝트 개요

## 프로젝트 정보
- **프로젝트명**: CardNews Editor
- **목적**: 카드뉴스 및 유튜브/SNS 썸네일 전용 이미지 편집 자동화 프로그램
- **플랫폼**: Windows 전용
- **언어**: Python 3.11+
- **UI 프레임워크**: PyQt6
- **배포 형식**: .exe (PyInstaller)

---

## 아키텍처

```
cardnews_editor/
├── main.py                  # 진입점
├── app/
│   ├── __init__.py
│   ├── main_window.py       # 메인 윈도우
│   ├── canvas/
│   │   ├── canvas_widget.py # 편집 캔버스 (PyQt6 QGraphicsScene)
│   │   ├── image_item.py    # 드래그/리사이즈 가능한 이미지 레이어
│   │   └── text_item.py     # 드래그/편집 가능한 텍스트 레이어
│   ├── template/
│   │   ├── template_manager.py  # 템플릿 CRUD
│   │   └── template_model.py    # 템플릿 데이터 모델
│   ├── panels/
│   │   ├── toolbar.py       # 상단 툴바
│   │   ├── property_panel.py # 우측 속성 패널 (텍스트 색상, 폰트 등)
│   │   └── layer_panel.py   # 레이어 순서 패널
│   ├── batch/
│   │   ├── batch_dialog.py  # 대량 처리 다이얼로그
│   │   └── batch_processor.py # CSV/Excel + 폴더 기반 배치 처리
│   └── export/
│       └── exporter.py      # JPG / PNG / WEBP 내보내기
├── assets/
│   └── icons/               # UI 아이콘
├── templates/               # 저장된 템플릿 파일 (.json)
├── requirements.txt
├── build.bat                # PyInstaller 빌드 스크립트
├── claude.md
├── skills.md
└── devbug.md
```

---

## 핵심 기능 명세

### 1. 템플릿 시스템
- 캔버스 크기 설정: 사전 정의 규격 + 사용자 지정
- 이미지 슬롯 배치 (화면 분할 레이아웃)
- 텍스트 박스 배치 (위치, 폰트, 색상, 크기 저장)
- 배경색/배경이미지 설정
- 템플릿 저장: JSON 포맷 (templates/*.json)

### 2. 편집 기능
- 템플릿 불러오기
- 이미지 슬롯에 이미지 파일 드래그 앤 드롭 또는 클릭 선택
- 이미지 마우스 드래그로 위치/크기 조정
- 텍스트 더블클릭 편집
- 텍스트 색상, 폰트, 크기 실시간 변경
- PC 설치 폰트 목록 불러오기

### 3. 표준 캔버스 규격
| 용도 | 크기 |
|------|------|
| 인스타그램 정방형 | 1080 × 1080 |
| 인스타그램 세로형 | 1080 × 1350 |
| 유튜브 썸네일 | 1280 × 720 |
| 블로그 썸네일 | 800 × 450 |
| 카카오채널 | 1000 × 1000 |
| 사용자 지정 | 자유 입력 |

### 4. 파일 저장
- 포맷: .jpg, .png, .webp
- 품질 설정 (JPG/WEBP: 1~100)
- 저장 경로 지정

### 5. 대량 처리 (배치)
- **폴더 기반**: 이미지 폴더 선택 → 템플릿 슬롯에 자동 매핑 → 일괄 저장
- **CSV/Excel 기반**: 텍스트 데이터 컬럼 → 템플릿 텍스트 슬롯에 자동 매핑 → 일괄 생성
- 진행률 표시 (QProgressBar)

---

## 기술 스택

| 역할 | 라이브러리 |
|------|-----------|
| UI | PyQt6 |
| 이미지 처리 | Pillow (PIL) |
| 캔버스 렌더링 | PyQt6 QGraphicsScene/View |
| Excel 처리 | openpyxl |
| CSV 처리 | pandas |
| 빌드 (.exe) | PyInstaller |
| 폰트 목록 | PyQt6 QFontDatabase |

---

## 개발 단계

| 단계 | 내용 | 상태 |
|------|------|------|
| 1 | 프로젝트 구조 세팅 + 메인 윈도우 | ⬜ |
| 2 | 캔버스 + 이미지/텍스트 레이어 | ⬜ |
| 3 | 템플릿 생성/저장/불러오기 | ⬜ |
| 4 | 속성 패널 (폰트, 색상, 크기) | ⬜ |
| 5 | 파일 내보내기 (다중 포맷) | ⬜ |
| 6 | 배치 처리 (폴더 + CSV/Excel) | ⬜ |
| 7 | PyInstaller .exe 빌드 | ⬜ |
| 8 | 테스트 및 버그 수정 | ⬜ |
