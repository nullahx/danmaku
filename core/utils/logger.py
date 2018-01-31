import os
import logging
from datetime import date, datetime


class Logger(object):
    LOG_FOLDER = os.path.join(
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(__file__)
            )
        ),
        'logs'
    )
    file_prefix = 'log_'
    file_postfix = '.txt'

    """Level of logger"""
    NORMAL = (0, 'MESSAGE')
    DEBUG = (1, 'DEBUG')
    ERROR = (2, 'ERROR')

    def __int__(self):
        raise Exception('Logger类不可被实例化')

    @classmethod
    def logf(cls, content, level=None):
        if not level:
            level = cls.NORMAL
        logging.debug(content)
        file_name = os.path.join(cls.LOG_FOLDER, cls.file_prefix + str(date.today()) + cls.file_postfix)
        with open(file_name, 'a', encoding='utf-8') as f:
            f.write(str(datetime.now()) + '\t' + level[1] + '\t' + content)
            f.write('\n')

    @classmethod
    def logd(cls, content, level):
        if not level:
            level = cls.NORMAL
        if level == cls.NORMAL:
            pass
        elif level == cls.DEBUG:
            logging.debug(str(datetime.now()) + '\t' + level[1] + '\t' + content)
        elif level == cls.ERROR:
            logging.error(str(datetime.now()) + '\t' + level[1] + '\t' + content)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    Logger.logf('Hello World', level=Logger.DEBUG)