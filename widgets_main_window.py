# widgets_main_window.py
"""
主窗口模块 - 实现带毛玻璃效果的现代化主界面

包含功能：
- 可拖拽的毛玻璃效果窗口
- 始终置顶显示
- 功能按钮和文本显示区域
"""
from window_frosted_glass import FrostedGlassWidget
from PySide6.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QMessageBox
from PySide6.QtCore import Qt
from widgets_draggable import DraggableMixin
from widgets_frosted_message_box import FrostedMessageBox
from config_manager import load_config


class ModernWindow(DraggableMixin, FrostedGlassWidget):
    """
    现代化主窗口类，继承可拖拽和毛玻璃效果特性

    特性：
    - 可拖拽的标题栏区域
    - 毛玻璃透明效果
    - 始终置顶显示
    - 功能按钮和文本显示区域
    """

    # 主窗体尺寸常量
    WINDOW_SIZE = (260, 320)

    # 按钮样式表
    BUTTON_STYLE = {
        "min": """
            QPushButton { 
                background-color: #FFBD2E; 
                border-radius: 6px; 
            }
            QPushButton:hover { 
                background-color: #FF9F00; 
            }
        """,
        "close": """
            QPushButton { 
                background-color: #FF5F56; 
                border-radius: 6px; 
            }
            QPushButton:hover { 
                background-color: #FF3B30; 
            }
        """,
        "action": """
            QPushButton { 
                background-color: #5F9EA0; 
                border-radius: 10px;
                padding: 8px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover { 
                background-color: #4682B4;
            }
            QPushButton:pressed {
                background-color: #4169E1;
            }
        """
    }

    def __init__(self):
        FrostedGlassWidget.__init__(self)
        DraggableMixin.__init__(self)

        self._setup_window_properties()
        self._init_ui()
        self._load_window_position()

    def _load_window_position(self):
        """加载窗口位置"""
        try:
            config = load_config()
            default_pos = [200, 200]
            pos = config.get("window_position", default_pos)

            screen = QApplication.primaryScreen()
            if not screen:
                self.move(*default_pos)
                return

            screen_geo = screen.availableGeometry()
            max_x = screen_geo.right() - self.width()
            max_y = screen_geo.bottom() - self.height()
            x = min(max(pos[0], screen_geo.left()), max_x)
            y = min(max(pos[1], screen_geo.top()), max_y)

            self.move(int(x), int(y))
        except Exception as e:
            print(f"加载窗口位置失败: {str(e)}")
            self.move(100, 100)

    def _setup_window_properties(self):
        """设置窗口基本属性"""
        self.setWindowTitle("工具")
        self.setFixedSize(*self.WINDOW_SIZE)
        # 设置窗口始终置顶
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

    def _init_ui(self):
        """初始化用户界面"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 添加界面组件
        main_layout.addLayout(self._create_top_bar())  # 顶部控制栏
        main_layout.addWidget(self._create_text_display())  # 文本显示框
        main_layout.addLayout(self._create_button_group())  # 按钮组（在文本框下面）
        main_layout.addStretch(1)

        self.setLayout(main_layout)

    def _create_top_bar(self):
        """创建顶部控制栏布局"""
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 15)

        # 标题标签
        title = self._create_label("分销商对账", font_size=12, bold=True)
        top_bar.addStretch(1)
        top_bar.addWidget(title, alignment=Qt.AlignCenter)
        top_bar.addStretch(1)

        # 窗口控制按钮
        control_buttons = QHBoxLayout()
        control_buttons.addWidget(
            self._create_control_button("min", self.showMinimized)
        )
        control_buttons.addWidget(
            self._create_control_button("close", self.close)
        )

        top_bar.addLayout(control_buttons)
        return top_bar

    def _create_text_display(self):
        """创建文本显示框"""
        self.text_display = QTextEdit()
        self.text_display.setFixedHeight(150)
        self.text_display.setStyleSheet("""
            QTextEdit {
                background: rgba(255, 255, 255, 120);
                border: 1px solid #4682B4;
                border-radius: 10px;
                padding: 8px;
                color: #2F4F4F;
                font-family: "Microsoft YaHei";
                font-size: 10px;
            }
            QTextEdit:focus {
                border: 1px solid #1E90FF;
            }
        """)
        self.text_display.setReadOnly(True)

        # 设置初始提示文本
        initial_text = """欢迎使用！

功能说明：
• 功能一：执行第一个操作
• 功能二：执行第二个操作

请点击下方按钮开始使用..."""
        self.text_display.setText(initial_text)

        return self.text_display

    def _create_button_group(self):
        """创建按钮组布局（在文本框下面）"""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # 创建两个功能按钮
        btn1 = self._create_action_button("功能一", self.on_button1_clicked)
        btn2 = self._create_action_button("功能二", self.on_button2_clicked)

        button_layout.addWidget(btn1)
        button_layout.addWidget(btn2)

        return button_layout

    def _create_control_button(self, btn_type, callback):
        """创建控制按钮"""
        btn = QPushButton()
        btn.setFixedSize(12, 12)
        btn.setStyleSheet(self.BUTTON_STYLE[btn_type])
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(callback)
        return btn

    def _create_action_button(self, text, callback):
        """创建功能按钮"""
        btn = QPushButton(text)
        btn.setFixedHeight(35)
        btn.setStyleSheet(self.BUTTON_STYLE["action"])
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(callback)
        return btn

    def _create_label(self, text, font_size=10, bold=False):
        """创建标签"""
        label = QLabel(text)
        font = label.font()
        font.setFamily("Microsoft YaHei")
        font.setPointSize(font_size)
        font.setBold(bold)
        label.setFont(font)
        label.setStyleSheet("color: #2F4F4F;")
        return label

    def on_button1_clicked(self):
        """功能一按钮点击事件"""
        # self.text_display.append("✅ 功能一已执行")

    def on_button2_clicked(self):
        """功能二按钮点击事件"""
        self.text_display.append("✅ 功能二已执行")

    def show_message(self, title, text, icon=QMessageBox.Warning):
        """显示毛玻璃风格消息弹窗"""
        FrostedMessageBox(self, title, text, icon).exec()

    def closeEvent(self, event):
        """窗口关闭事件 - 保存当前位置"""
        from config_manager import set_config_value
        try:
            pos = [self.pos().x(), self.pos().y()]
            set_config_value("window_position", pos)
        except Exception as e:
            print(f"保存窗口位置失败: {str(e)}")
        event.accept()