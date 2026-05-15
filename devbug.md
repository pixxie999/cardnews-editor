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

<!-- 이후 작업 진행하면서 아래에 계속 추가 -->
