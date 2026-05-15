import sys
import platform
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QFontDatabase
from app.main_window import MainWindow


def _pick_korean_font(app: QApplication) -> str:
    """OS별 기본 한국어 폰트 반환"""
    available = set(QFontDatabase.families())
    candidates = {
        "Windows": ["맑은 고딕", "굴림", "돋움"],
        "Darwin":  ["Apple SD Gothic Neo", "Nanum Gothic", "AppleGothic"],
        "Linux":   ["Noto Sans CJK KR", "Nanum Gothic", "UnDotum"],
    }
    os_key = platform.system()
    for name in candidates.get(os_key, []):
        if name in available:
            return name
    return ""   # 시스템 기본값 사용


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("CardNews Editor")
    app.setOrganizationName("uasoft")

    # OS별 한국어 폰트 자동 선택
    font_name = _pick_korean_font(app)
    if font_name:
        app.setFont(QFont(font_name, 10))

    # 다크 팔레트는 기본값 사용 (시스템 테마 따름)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
