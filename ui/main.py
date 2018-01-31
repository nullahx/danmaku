import threading
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QTextEdit, QWidget, QLabel, QLineEdit
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from core.assist import PandaAPI
from core.message import BaseMessage, Message, AnimationGift, BambooGift, RoomInfo


class MainPandaTV(QMainWindow):
    room_id = 0
    message = pyqtSignal(BaseMessage)
    people_num = pyqtSignal(str, str)
    target_work = None
    _is_stopped = False

    def __init__(self, room_id, parent=None):
        super().__init__(parent=parent)
        self.parent_window = parent
        self.main_widget = QWidget()
        # 消息展示暂时用的文本框，不太合理，之后再改
        self.danmu_box = QTextEdit()
        self.room_id = room_id
        self.target_work = None
        self.room_id_display = QLineEdit(self.tr(str(self.room_id)))
        self.current_people_display = QLineEdit()
        self.total_people_display = QLineEdit()
        self.init_ui()
        self.init_slot()
        self.setWindowTitle('PandaTv 弹幕助手v0.1')
        self._is_stopped = False
        self.init_content()
        self.background_work()

    def init_ui(self):
        sub_layout = QHBoxLayout()
        main_layout = QVBoxLayout()

        room_id_label = QLabel(self.tr('房间号'))
        current_people_label = QLabel(self.tr('当前人数'))
        total_people_label = QLabel(self.tr('累计人数'))
        room_id_label.setBuddy(self.room_id_display)
        current_people_label.setBuddy(self.current_people_display)
        total_people_label.setBuddy(self.total_people_display)

        sub_layout.addWidget(room_id_label)
        sub_layout.addWidget(self.room_id_display)
        sub_layout.addWidget(current_people_label)
        sub_layout.addWidget(self.current_people_display)
        sub_layout.addWidget(total_people_label)
        sub_layout.addWidget(self.total_people_display)

        main_layout.addLayout(sub_layout)
        main_layout.addWidget(self.danmu_box)
        self.main_widget.setLayout(main_layout)
        self.setCentralWidget(self.main_widget)
        self.setFixedHeight(500)

    def init_slot(self):
        self.message.connect(self.updateMessage)
        self.people_num.connect(self.updatePeople)

    def init_content(self):
        self.room_id_display.setEnabled(False)
        self.current_people_display.setEnabled(False)
        self.total_people_display.setEnabled(False)

    def background_work(self):
        panda = PandaAPI(self.room_id)
        panda.login()
        panda.mainloop()

        def back_work():
            while not self._is_stopped:
                msg = panda.get_message()
                self.message.emit(msg)
            panda.exit()
        self.target_work = threading.Thread(
            target=back_work, name='master thread')
        self.target_work.setDaemon(True)
        self.target_work.start()

    def closeEvent(self, QCloseEvent):
        if self.target_work.is_alive():
            self._is_stopped = True
        if self.parent_window:
            self.parent_window.show()

    @pyqtSlot(str, str, name='update_people')
    def updatePeople(self, current_people, total_people):
        self.current_people_display.setText(current_people)
        self.total_people_display.setText(total_people)

    @pyqtSlot(BaseMessage, name='update_message')
    def updateMessage(self, msg: BaseMessage):
        if isinstance(msg, Message):
            self.danmu_box.insertHtml('<span style="color:red">{0}</span>'
                                      '<span style="color:#04c073;">{1}</span>'
                                      '<span style="color:black">{2}</span><br>'
                                      .format(str(msg.from_where['level']),
                                              str(msg.from_where['nickname']),
                                              str(msg.content)))
        elif isinstance(msg, AnimationGift):
            self.danmu_box.insertHtml('<span style="color:#ff7608">{0}</span>'
                                      '<span style="color:black">送出</span>'
                                      '<span style="color:#04c073;">{1}</span>'
                                      '<span style="color:black">个</span>'
                                      '<span style="color:blue">{2}</span><br>'
                                      .format(str(msg.from_where['nickname']),
                                              str(msg.content['count']),
                                              str(msg.content['gift_name'])))
        elif isinstance(msg, BambooGift):
            self.danmu_box.insertHtml('<span style="color:#04c073;">{0}</span>'
                                      '<span style="color:black">送出</span>'
                                      '<span style="color:#04c073;">{1}</span>'
                                      '<span style="color:black">个</span>'
                                      '<span style="color:#04c073;">{2}</span><br>'
                                      .format(str(msg.from_where['nickname']),
                                              str(msg.content['count']),
                                              str(msg.content['gift_name'])))
        elif isinstance(msg, RoomInfo):
            self.people_num.emit(
                str(msg.content['show_num']), str(msg.content['total']))
