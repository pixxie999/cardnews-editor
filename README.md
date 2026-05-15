# CardNews Editor

카드뉴스 및 SNS 썸네일 자동화 편집 프로그램 (Windows 전용)

## 주요 기능
- 템플릿 생성/저장/불러오기 (이미지 슬롯 + 텍스트 배치)
- 마우스 기반 이미지 위치/크기 조정
- 한국어 폰트 지원 (PC 설치 폰트)
- JPG / PNG / WEBP 내보내기
- 대량 처리: 폴더 기반 + CSV/Excel 기반

## 설치 및 실행

```bash
pip install -r requirements.txt
python main.py
```

## .exe 빌드

```bash
build.bat
```

## 기술 스택
- UI: PyQt6
- 이미지 처리: Pillow
- 데이터: pandas, openpyxl
- 빌드: PyInstaller
