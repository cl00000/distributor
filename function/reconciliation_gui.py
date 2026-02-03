# function/reconciliation_gui.py
from PySide6.QtCore import QThread, Signal, QMutex


class ReconciliationWorker(QThread):
    """对账工作线程"""
    # 定义信号
    output_signal = Signal(str)  # 输出消息信号
    finished_signal = Signal(bool, str)  # 完成信号（成功/失败，消息）

    def __init__(self):
        super().__init__()
        self._mutex = QMutex()
        self._running = True

    @property
    def running(self):
        """线程运行状态（线程安全获取）"""
        self._mutex.lock()
        value = self._running
        self._mutex.unlock()
        return value

    @running.setter
    def running(self, value):
        """设置线程运行状态（线程安全设置）"""
        self._mutex.lock()
        self._running = value
        self._mutex.unlock()

    def run(self):
        """线程执行函数"""
        try:
            # 导入对账模块
            from function.reconciliation import run_reconciliation_with_gui

            # 定义输出回调函数
            def output_callback(message):
                if self.running:
                    self.output_signal.emit(message)

            # 运行对账功能
            if self.running:
                self.output_signal.emit("开始执行对账处理...")
                self.output_signal.emit("=" * 24)

            if self.running:
                success = run_reconciliation_with_gui(output_callback)

                if success:
                    self.finished_signal.emit(True, "✅ 对账处理完成！")
                else:
                    self.finished_signal.emit(False, "❌ 对账处理失败！")

        except ImportError as e:
            if self.running:
                self.output_signal.emit(f"❌ 导入模块失败: {str(e)}")
                self.finished_signal.emit(False, f"❌ 导入模块失败: {str(e)}")
        except Exception as e:
            if self.running:
                self.output_signal.emit(f"❌ 执行过程中发生错误: {str(e)}")
                self.finished_signal.emit(False, f"❌ 执行过程中发生错误: {str(e)}")

    def stop(self):
        """停止线程"""
        self.running = False