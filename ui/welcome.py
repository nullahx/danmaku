from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QLabel, QLineEdit, QHBoxLayout, QPushButton, QMessageBox
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from ui.main import MainPandaTV


class PandaTv(QDialog):
    #子窗口实例
    main_window = None

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.input_room = QLineEdit()
        self.confirm_button = QPushButton(self.tr('进入'))
        self.init_ui()
        self.init_slot()

    def init_ui(self):
        self.setWindowTitle(self.tr('Panda Tv Damu'))
        label = QLabel(self.tr('房间号'))
        label.setBuddy(self.input_room)
        main_layout = QHBoxLayout()
        main_layout.addWidget(label)
        main_layout.addWidget(self.input_room)
        main_layout.addWidget(self.confirm_button)
        self.setLayout(main_layout)

    def init_slot(self):    #信号与槽建立连接
        self.confirm_button.clicked.connect(self.on_confirm_button_clicked)

    @pyqtSlot(name='confirm_button_click')     #定义一个槽，用于接收来自确认按钮的信号，并打开主窗口
    def on_confirm_button_clicked(self):
        room_id = self.input_room.text()
        if not room_id:
            msg = QMessageBox.information(self, None, '<center><h2>❌</h2> <p>房间号不能为空！</p><center>', QMessageBox.Ok)
        else:
            self.main_window = MainPandaTV(room_id, self)
            self.main_window.show()
            self.hide()

    def start(self):
        self.show()


#测试代码
if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    w = PandaTv()
    w.show()
    sys.exit(app.exec_())

