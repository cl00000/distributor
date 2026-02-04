# widgets_main_window.py
"""
主窗口模块 - 实现带毛玻璃效果的现代化主界面
"""
from window_frosted_glass import FrostedGlassWidget
from PySide6.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit
from PySide6.QtCore import Qt
from widgets_draggable import DraggableMixin
from config_manager import get_config_value, set_config_value


class ModernWindow(DraggableMixin, FrostedGlassWidget):
    """
    现代化主窗口类，继承可拖拽和毛玻璃效果特性
    """

    # 主窗体尺寸常量
    WINDOW_SIZE = (260, 350)

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

        # 存储按钮引用
        self.btn_function1 = None
        self.btn_function2 = None
        self.reconciliation_thread = None
        self._is_closing = False  # 添加关闭标志

        self._setup_window_properties()
        self._init_ui()
        self._load_window_position()

    def _load_window_position(self):
        """加载窗口位置"""
        try:
            config = get_config_value("window_position", [200, 200])
            default_pos = [200, 200]
            pos = config if isinstance(config, list) and len(config) == 2 else default_pos

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
        self.setWindowTitle("分销商对账工具")
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
        self.text_display.setFixedHeight(200)
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
        initial_text = """分销商对账工具 v2.0

功能说明：
• 功能一：执行分销商数据对账
• 功能二：汇总对账数据

请点击下方按钮开始使用..."""
        self.text_display.setText(initial_text)

        return self.text_display

    def _create_button_group(self):
        """创建按钮组布局（在文本框下面）"""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # 创建两个功能按钮
        self.btn_function1 = self._create_action_button("开始对账", self.on_button1_clicked)
        self.btn_function2 = self._create_action_button("数据汇总", self.on_button2_clicked)

        button_layout.addWidget(self.btn_function1)
        button_layout.addWidget(self.btn_function2)

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
        """功能一按钮点击事件 - 执行对账功能"""
        try:
            # 清空文本框
            self.text_display.clear()
            self.text_display.append("=" * 24)

            # 检查是否有正在运行的任务
            if self.reconciliation_thread and self.reconciliation_thread.isRunning():
                self.text_display.append("⚠ 已有任务正在运行，请等待完成...")
                return

            # 禁用按钮，防止重复点击
            self.btn_function1.setEnabled(False)
            self.btn_function2.setEnabled(False)

            # 动态导入，避免循环导入
            try:
                from function.reconciliation_gui import ReconciliationWorker
            except ImportError as e:
                self.text_display.append(f"❌ 导入模块失败: {str(e)}")
                self.text_display.append("请确保 function/reconciliation_gui.py 文件存在")
                # 重新启用按钮
                self.btn_function1.setEnabled(True)
                self.btn_function2.setEnabled(True)
                return

            # 创建工作线程
            self.reconciliation_thread = ReconciliationWorker()

            # 连接信号
            self.reconciliation_thread.output_signal.connect(self.update_output_display)
            self.reconciliation_thread.finished_signal.connect(self.on_reconciliation_finished)

            # 启动线程
            self.reconciliation_thread.start()

        except Exception as e:
            self.text_display.append(f"❌ 启动对账任务失败: {str(e)}")
            import traceback
            traceback.print_exc()

            # 确保按钮被重新启用
            self.btn_function1.setEnabled(True)
            self.btn_function2.setEnabled(True)

    def update_output_display(self, message):
        """更新输出显示"""
        if self.text_display:
            self.text_display.append(message)
            # 滚动到底部
            scrollbar = self.text_display.verticalScrollBar()
            if scrollbar:
                scrollbar.setValue(scrollbar.maximum())

    # 在 widgets_main_window.py 的 on_reconciliation_finished 方法中添加
    def on_reconciliation_finished(self, success, message):
        """开始对账完成回调"""
        if self.text_display:
            self.text_display.append("=" * 24)
            self.text_display.append(message)

            # 如果有错误，添加处理建议
            if not success and "多个'商家编码'字段" in self.text_display.toPlainText():
                self.text_display.append("\n💡 处理建议：")
                self.text_display.append("1. 请打开Excel文件检查列名")
                self.text_display.append("2. 确保只有一个名为'商家编码'的列")
                self.text_display.append("3. 修改后重新执行对账处理")

        # 重新启用按钮
        self.btn_function1.setEnabled(True)
        self.btn_function2.setEnabled(True)

        # 清理线程引用
        self.reconciliation_thread = None

    def on_button2_clicked(self):
        try:
            self.text_display.append("开始执行【售后汇总】...")
            self.text_display.append("=" * 24)

            from function.summary import run_summary

            def output_callback(msg):
                self.update_output_display(msg)

            success = run_summary(output_callback)

            if success:
                self.text_display.append("✅ 售后汇总完成！")
            else:
                self.text_display.append("❌ 售后汇总失败！")

        except Exception as e:
            self.text_display.append(f"❌ 执行失败：{e}")

    def closeEvent(self, event):
        """窗口关闭事件 - 保存当前位置"""
        try:
            self._is_closing = True

            # 停止正在运行的线程
            if self.reconciliation_thread and self.reconciliation_thread.isRunning():
                print("正在停止工作线程...")
                self.reconciliation_thread.stop()
                self.reconciliation_thread.quit()
                if not self.reconciliation_thread.wait(2000):  # 等待2秒
                    print("线程未正常停止，强制终止...")
                    self.reconciliation_thread.terminate()
                    self.reconciliation_thread.wait()

            # 保存窗口位置
            pos = [self.pos().x(), self.pos().y()]
            set_config_value("window_position", pos)

        except Exception as e:
            print(f"关闭窗口时发生错误: {str(e)}")
        finally:
            event.accept()
            QApplication.quit()  # 确保完全退出