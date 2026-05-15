import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from app.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("CardNews Editor")
    app.setOrganizationName("uasoft")

    # 기본 한국어 폰트 설정
    font = QFont("맑은 고딕", 10)
    app.setFont(font)

    # 다크 팔레트는 기본값 사용 (시스템 테마 따름)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
