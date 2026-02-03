# main.py (应用启动文件)
import sys
from PySide6.QtWidgets import QApplication
from widgets_main_window import ModernWindow


def main():
    app = QApplication(sys.argv)

    # 创建主窗口
    window = ModernWindow()
    window.show()

    # 启动应用
    sys.exit(app.exec())


if __name__ == "__main__":
    main()