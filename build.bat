@echo off
echo CardNews Editor - PyInstaller 빌드 시작
echo.

REM 이전 빌드 정리
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist CardNewsEditor.spec del CardNewsEditor.spec

REM PyInstaller 빌드
pyinstaller ^
  --onefile ^
  --windowed ^
  --name "CardNewsEditor" ^
  --add-data "assets;assets" ^
  --add-data "templates;templates" ^
  --hidden-import "PIL._tkinter_finder" ^
  --hidden-import "pandas" ^
  --hidden-import "openpyxl" ^
  main.py

echo.
if exist dist\CardNewsEditor.exe (
    echo [성공] dist\CardNewsEditor.exe 생성 완료
) else (
    echo [실패] 빌드에 실패했습니다. 위 오류를 확인하세요.
)
pause
