import time
import socket
import struct
import queue
import threading
from core.utils.logger import Logger
from core.message import MessageFactory
from core.utils.downloader import Downloader
from core.utils.utils import format_json_to_pytype

"""
    author: byken
    name: PandaDaMu v0.1
    注意: 挂代理时收不到弹幕信息
"""


class PandaAPI(object):
    _is_stopped = False
    target_work = None
    target_heart_break = None

    MAX_RECV_BUFFER = 4096
    HEART_BREAK_TIME = 180

    PACKAGE_PREFIX_LENGTH = 15
    PACKAGE_PREFIX_START = 11
    PACKAGE_PREFIX_END = 15
    PACKAGE_START = b'\x00\x06\x00\x03'

    #直播间弹幕服务信息获取
    sock = None

    room_api = "https://riven.panda.tv/chatroom/getinfo?roomid={0}&app=1&protocol=ws&_caller=panda-pc_web&_={1}"
    msg = "u:{0}@{1}\nk:1\nt:300\nts:{2}\nsign:{3}\nauthtype:{4}"

    room_id = 0
    room_info = \
    {
        'rid': int(),
        'app_id': int(),
        'time_stamp': 0,
        'sign': '',
        'auth_type': None,
        'server_list': list(),
    }

    server_has_select = 0
    heart_keeper = b'\x00\x06\x00\x01'
    message_list = queue.Queue(maxsize=500)

    recv_buffer = None

    #初始化房间信息
    def __init__(self, room_id=None):
        """
        :param roomid: 直播间房间号（int）
        """
        self._is_ready = False
        self._is_stopped = False
        self.danmu_uri = None
        if room_id:
            self.room_id = str(room_id)
            self.room_info['ts'] = int(time.time())
            self.danmu_uri = self.room_api.format(self.room_id, self.room_info['ts'])
            self.ready()

    def is_ready(self):
        return self._is_ready

    def ready(self):
        """
        通过获取房间信息，用于创立websocket连接
        """
        j_data = Downloader.get(self.danmu_uri).decode('utf-8')
        info = format_json_to_pytype(j_data)
        room_info = info['data']
        self.room_info['rid'] = room_info['rid']
        self.room_info['app_id'] = room_info['appid']
        self.room_info['time_stamp'] = room_info['ts']
        self.room_info['sign'] = room_info['sign']
        self.room_info['auth_type'] = room_info['authType']
        self.room_info['server_list'] = room_info['chat_addr_list']
        self._is_ready = True

    def _get_server(self):
        """
        未完成功能，连接不好时，自动切换服务器
        """
        if not self.room_info['server_list']:
            raise Exception('程序未初始化！')
        elif self.server_has_select <= len(self.room_info['server_list'])-1:
            server = self.room_info['server_list'][self.server_has_select]
            self.server_has_select += 1
            addr = server.rsplit(':')
            return addr[0], int(addr[1])
        elif self.server_has_select > len(self.room_info['server_list']):
            raise Exception('服务器皆不可用！')

    def login(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # 阻塞式socket
        self.sock.connect(self._get_server())
        msg = self.msg.format(self.room_info['rid'], self.room_info['app_id'], self.room_info['time_stamp'],
                              self.room_info['sign'], self.room_info['auth_type'])
        msg_prefix = b'\x00\x06\x00\x02\x00' + bytes([len(msg), ])
        msg_postfix = b'\x00\x06\x00\x00'
        self.sock.send(msg_prefix + msg.encode('utf-8'))
        self.sock.send(msg_postfix)
        print('弹幕服务登录成功！\t房间号：' + str(self.room_id))

        self.sock.recv(self.MAX_RECV_BUFFER)    # 服务器返回\x00\x06\x00\x06
        #获取心跳包
        self.heart_keeper = self.sock.recv(self.MAX_RECV_BUFFER)
        Logger.logd('heart break:{}'.format(self.heart_keeper), level=Logger.DEBUG)

    def mainloop(self):
        def _main_loop():
            """ 消息接收线程，将消息加入拥塞队列 """
            while not self._is_stopped:
                self.recv_buffer = self.sock.recv(self.PACKAGE_PREFIX_LENGTH)
                if not self.recv_buffer or not self.recv_buffer.startswith(self.PACKAGE_START):
                    continue
                package_length = struct.unpack(
                    '>I', self.recv_buffer[
                          self.PACKAGE_PREFIX_START:
                          self.PACKAGE_PREFIX_END
                          ])[0]
                print('package length: ', package_length)
                print(len(self.recv_buffer))
                while package_length:
                    self.recv_buffer = self.sock.recv(MessageFactory.MESSAGE_PREFIX_LENGTH)
                    message_length = struct.unpack(
                        '>I', self.recv_buffer[
                              MessageFactory.MESSAGE_PREFIX_START:
                              MessageFactory.MESSAGE_PREFIX_END
                              ])[0]
                    print(self.recv_buffer)
                    print('message length: ', message_length)
                    self.recv_buffer = self.sock.recv(message_length)
                    while not len(self.recv_buffer) == message_length:
                        self.recv_buffer += self.sock.recv(message_length - len(self.recv_buffer))
                    Logger.logd(str(self.recv_buffer), level=Logger.DEBUG)
                    msg = MessageFactory.get_message(self.recv_buffer)
                    if msg:
                        self.message_list.put(msg)
                    package_length -= (message_length + MessageFactory.MESSAGE_PREFIX_LENGTH)
            self.sock.close()
        self.target_work = threading.Thread(target=_main_loop, name='target_work')
        # 设定子线程为守护线程，保证在socket拥塞的情况下能正常退出
        self.target_work.setDaemon(True)
        self.target_work.start()

        self.target_heart_break = threading.Thread(target=self._heart_break, name='heart_break')
        # 设定心跳包发送进程为守护进程，保证在一直未接到消息时心跳包发送不会停止
        self.target_heart_break.setDaemon(True)
        self.target_heart_break.start()

    def _heart_break(self):
        """ 心跳包，默认3分钟 """
        start_stamp = int(time.time())
        while not self._is_stopped:
            if int(time.time() - start_stamp) <= self.HEART_BREAK_TIME:
                continue
            self.sock.send(self.heart_keeper)

    def get_room(self):
        return self.room_id

    def set_room(self, room_id):
        self.room_id = room_id
        self.room_info['ts'] = int(time.time())
        self.danmu_uri = self.room_api.format(self.room_id, self.room_info['ts'])

    def get_message(self):
        """ -> msg(BaseMessage) """
        #拥塞队列消息
        return self.message_list.get(block=True)

    def exit(self):
        """ 将关状态设置为True，由线程自动退出 """
        self._is_stopped = True
        self.sock.shutdown(socket.SHUT_RDWR)


if __name__ == '__main__':
    import logging
    # logging.basicConfig(level=logging.DEBUG)
    panda = PandaAPI(20641)
    panda.login()
    panda.mainloop()
    while True:
        print(panda.get_message())
