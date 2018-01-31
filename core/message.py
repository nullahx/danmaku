from core.utils.logger import Logger
from core.utils.utils import format_json_to_pytype, JSONDecodeError
from abc import ABCMeta, abstractmethod

"""
    #消息类及消息获取格式化的类
"""

#TEST_MSG = {}

#用户等级字典
USER_LEVEL = {
    1: '青铜5', 2: '青铜4', 3: '青铜3', 4: '青铜2', 5: '青铜1',
    6: '白银5', 7: '白银4', 8: '白银3', 9: '白银2', 10: '白银1',
    11: '黄金5', 12: '黄金4', 13: '黄金3', 14: '黄金2', 15: '黄金1',
    16: '铂金5', 17: '铂金4', 18: '铂金3', 19: '铂金2', 20: '铂金1',
    21: '钻石5', 22: '钻石4', 23: '钻石3', 24: '钻石2', 25: '钻石1',
    26: '宗师5', 27: '宗师4', 28: '宗师3', 29: '宗师2', 30: '宗师1',
    31: '王者5', 32: '王者4', 33: '王者3', 34: '王者2', 35: '王者1',
    36: '史诗5', 37: '史诗4', 38: '史诗3', 39: '史诗2', 40: '史诗1',
}


#基础抽象消息类，包含消息必含的字段
class BaseMessage(object):
    __metaclass__ = ABCMeta
    raw_data = None
    m_type = 1
    m_length = 0
    data = None
    from_where = None
    to_where = None
    content = None

    def __init__(self, raw_data, length):
        self.raw_data = raw_data
        self.m_length = length

    def __str__(self):
        return 'From: {0}\n' \
               'To.: {1}\n' \
               'Msg: {2}'.format(
                    self.to_where,
                    self.from_where,
                    self.content
               )


# 普通消息，类型 --- 1
class Message(BaseMessage):
    def __init__(self, raw_data, length):
        super().__init__(raw_data, length)
        self.from_where = dict()
        self.to_where = dict()
        self.from_where['identity'] = raw_data['from']['identity']
        self.from_where['nickname'] = raw_data['from']['nickName']
        self.from_where['badge'] = raw_data['from']['badge']
        self.from_where['rid'] = raw_data['from']['rid']
        self.from_where['msgcolor'] = raw_data['from']['msgcolor']
        self.from_where['level'] = USER_LEVEL[int(raw_data['from']['level'])]
        self.from_where['sp_identity'] = raw_data['from']['sp_identity']
        self.from_where['__plat'] = raw_data['from']['__plat']
        self.from_where['username'] = raw_data['from']['__plat']
        self.to_where['toroom'] = raw_data['to']['toroom']
        self.content = raw_data['content']

    def __str__(self):
        return 'User: {0}\n' \
               'Level.{1}\n' \
               'To: Room.{2}\n' \
               'Msg: {3}'.format(
                    self.from_where['nickname'],
                    self.from_where['level'],
                    self.to_where['toroom'],
                    self.content
               )


# 类型 --- 100
class NoticeMessage(BaseMessage):
    def __init__(self, raw_data, length):
        super().__init__(raw_data, length)
        self.from_where = dict()
        self.to_where = dict()
        self.content = dict()
        self.from_where['nickname'] = raw_data['from']['nickName']
        self.from_where['rid'] = raw_data['from']['rid']
        self.to_where['toroom'] = raw_data['to']['toroom']
        self.content['forbid_rid'] = raw_data['content']['forbid_rid']
        self.content['msg'] = raw_data['content']['msg']
        self.content['show_notice'] = raw_data['content']['show_notice']
        self.content['type'] = raw_data['content']['type']
        self.content['unlock_time'] = raw_data['content']['unlock_time']


class BaseRoomInfo(BaseMessage):
    def __init__(self, raw_data, length):
        super().__init__(raw_data, length)
        self.from_where = dict()
        self.to_where = dict()
        try:
            self.from_where['rid'] = raw_data['from']['rid']
        except KeyError:
            pass
        self.to_where['toroom'] = raw_data['to']['toroom']


# 类型 --- 205
class RoomInfo(BaseRoomInfo):
    def __init__(self, raw_data, length):
        super().__init__(raw_data, length)
        self.content = dict()
        self.content['show_num'] = raw_data['content']['show_num']
        self.content['total'] = raw_data['content']['total']

    def __str__(self):
        return '当前房间人数: {0}, 累计: {1}. '.format(
            self.content['show_num'],
            self.content['total']
        )


# 类型 --- 207
class RoomInfoPeople(BaseRoomInfo):
    def __init__(self, raw_data, length):
        super().__init__(raw_data, length)
        self.content = raw_data['content']


# 类型 --- 208
class RoomInfoBamboo(BaseRoomInfo):
    def __init__(self, raw_data, length):
        super().__init__(raw_data, length)
        self.content = raw_data['content']


# 类型 --- 3003
class RoomInfoTicket(BaseRoomInfo):
    def __init__(self, raw_data, length):
        super().__init__(raw_data, length)
        self.content = dict()
        self.content['type'] = raw_data['content']['type']
        self.content['rank'] = raw_data['content']['rank']
        self.content['score'] = raw_data['content']['score']
        self.content['day_score'] = raw_data['content']['day_score']


# 类型 --- 212
class RoomInfoCount(BaseRoomInfo):
    def __init__(self, raw_data, length):
        super().__init__(raw_data, length)
        #当前经验值
        self.content = dict()
        self.content['val'] = raw_data['content']['val']
        #当前等级
        self.content['c_lv'] = raw_data['content']['c_lv']
        #当前等级需要经验值
        self.content['c_lv_val'] = raw_data['content']['c_lv_val']
        #下一等级
        self.content['n_lv'] = raw_data['content']['n_lv']
        #下一等级需要经验值
        self.content['n_lv_val'] = raw_data['content']['n_lv_val']
        #开播天数
        self.content['plays_day'] = raw_data['content']['plays_day']
        #竹子用户数
        self.content['bamboo_user'] = raw_data['content']['bamboo_user']
        #礼物用户数
        self.content['gift_user'] = raw_data['content']['gift_user']
        #礼物统计
        self.content['gift_cnt'] = raw_data['content']['gift_cnt']
        #vip等级
        self.content['vip'] = raw_data['content']['vip']
        # vip升级等级
        self.content['upgrade'] = raw_data['content']['upgrade']


# 类型 --- 206
class BambooGift(BaseMessage):
    def __init__(self, raw_data, length):
        super().__init__(raw_data, length)
        self.from_where = dict()
        self.to_where = dict()
        self.content = dict()
        self.from_where['identity'] = raw_data['from']['identity']
        self.from_where['nickname'] = raw_data['from']['nickName']
        self.from_where['rid'] = raw_data['from']['rid']
        self.from_where['sp_identity'] = raw_data['from']['sp_identity']
        self.to_where['toroom'] = raw_data['to']['toroom']
        self.content['count'] = raw_data['content']
        self.content['gift_name'] = '竹子'

    def __str__(self):
        return '{0} 送出 {1} 个 {2}'.format(
            self.from_where['nickname'],
            self.content['count'],
            self.content['gift_name']
        )


# 顶部礼物消息，类型 --- 306
class AnimationGift(BaseMessage):
    def __init__(self, raw_data, length):
        super().__init__(raw_data, length)
        self.from_where = dict()
        self.to_where = dict()
        self.content = dict()
        self.from_where['identity'] = raw_data['from']['identity']
        self.from_where['nickname'] = raw_data['from']['nickName']
        self.from_where['rid'] = raw_data['from']['rid']
        self.from_where['sp_identity'] = raw_data['from']['sp_identity']
        self.to_where['toroom'] = raw_data['to']['toroom']
        self.content['group'] = raw_data['content']['group']
        self.content['id'] = raw_data['content']['id']
        self.content['gift_name'] = raw_data['content']['name']
        self.content['count'] = raw_data['content']['count']

    def __str__(self):
        return '{0} 送出 {1} 个 {2}'.format(
            self.from_where['nickname'],
            self.content['count'],
            self.content['gift_name']
        )


#消息格式化类，不可被实例化
class MessageFactory(object):
    MESSAGE_PREFIX_LENGTH = 16
    MESSAGE_PREFIX_START = 12
    MESSAGE_PREFIX_END = 16

    TYPE = {
        '1': Message,
        '100': NoticeMessage,
        '205': RoomInfo,
        '206': BambooGift,
        '207': RoomInfoPeople,
        '208': RoomInfoBamboo,
        '306': AnimationGift,
        '212': RoomInfoCount,
        '3003': RoomInfoTicket,
    }

    def __init__(self):
        raise TypeError('MessageFactory类不可被实例化')

    @classmethod
    def get_message(cls, raw_data):
        print(raw_data)
        m_length = len(raw_data)
        j_data = format_json_to_pytype(raw_data)
        if j_data['type'] in cls.TYPE:
            msg = cls.TYPE[j_data['type']](j_data['data'], m_length)
        else:
            msg = None
        # print(msg)
        # print('*'*30)
        return msg


if __name__ == '__main__':
    msg = MessageFactory.get_message(
        b'\x00\x06\x00\x03\x00\x05ack:0'
        b'\x00\x00\x01y\x00\x00\x00\x00'
        b'\x00\x00\x00\x00\x00\x00\x00'
        b'\x00\x00\x00\x01i{"type":"1",'
        b'"time":1517067700,"data":{"from":'
        b'{"identity":"60","nickName":"Kobe'
        b'\xe4\xb8\xa8\xe9\x80\x8d\xe9\x81'
        b'\xa5\xe5\xb3\xb0\xe7\xa5\x9e",'
        b'"medal":{"level":12,"medal":"'
        b'\xe8\x8e\x93\xe5\xa4\xa7\xe5\x8f\x94",'
        b'"type":5,"active":1,"hid":5119934},'
        b'"badge":"60","rid":"78845282",'
        b'"msgcolor":"","hl":8,"level":"21",'
        b'"sp_identity":"30","__plat":"",'
        b'"userName":""},"to":{"toroom":"222223"},'
        b'"content":"\xe6\x9c\x89\xe5\x9c\xa8\xe5'
        b'\x9b\xbd\xe5\x86\x85\xe7\x9a\x84\xe6\x97'
        b'\xb6\xe5\xb7\xae\xe5\x85\x9a[:\xe5\x8a'
        b'\xaa\xe5\x8a\x9b][:\xe5\x8a\xaa\xe5\x8a\x9b]"}}'
    )
    print(msg)